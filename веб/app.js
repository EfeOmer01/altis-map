/* === ТАКТИЧЕСКАЯ КАРТА ARMA 3 ALTIS — v4 ПОЛНОЕ СООТВЕТСТВИЕ ИГРЕ === */

document.addEventListener('DOMContentLoaded', () => {

  // ======================================================================
  //  0. МГНОВЕННОЕ УПРАВЛЕНИЕ МОДАЛКАМИ HUD
  // ======================================================================
  const authModal  = document.getElementById('auth-modal');
  const squadModal = document.getElementById('squad-modal');

  function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('hidden');
  }
  function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  }

  function showAuthMsg(msg, type) {
    const el = document.getElementById('auth-status-msg');
    if (!el) return;
    el.textContent = msg;
    el.className = 'auth-status-msg ' + (type || '');
    el.classList.remove('hidden');
  }

  // Кнопка ВОЙТИ в HUD
  document.getElementById('btn-open-auth-modal')?.addEventListener('click', () => {
    openModal('auth-modal');
  });

  // Клик по профилю (если уже авторизован) -> открывает окно сквадов или профиля
  document.getElementById('user-profile-badge')?.addEventListener('click', (e) => {
    if (e.target && e.target.id === 'btn-logout') return;
    if (currentUser && currentUser.squadId) {
      openModal('squad-modal');
    } else {
      openModal('auth-modal');
    }
  });

  // Кнопка СКВАДЫ в HUD
  document.getElementById('btn-open-squad-modal')?.addEventListener('click', () => {
    if (!currentUser) {
      openModal('auth-modal');
      showAuthMsg('Сначала войдите в аккаунт, чтобы создать сквад или управлять отрядом!', 'warning');
      return;
    }
    openModal('squad-modal');
    if (authToken && typeof socket !== 'undefined' && socket) {
      socket.emit('auth_socket', { token: authToken });
    }
  });

  // Крестики закрытия модалок
  document.getElementById('modal-auth-close')?.addEventListener('click', () => closeModal('auth-modal'));
  document.getElementById('modal-squad-close')?.addEventListener('click', () => closeModal('squad-modal'));

  // ======================================================================
  //  1. КОНСТАНТЫ И СИСТЕМА КООРДИНАТ
  // ======================================================================
  const WORLD   = 30720;
  // Готовая топографическая подложка Altis имеет 144 условные единицы по стороне.
  // Все игровые координаты пересчитываются в неё без смещения.
  const CRS_MAX = 144;
  const K       = WORLD / CRS_MAX;

  function gameToLatLng(gx, gy) {
    return L.latLng((gy - WORLD) / K, gx / K);
  }
  function latLngToGame(ll) {
    return { x: Math.round(ll.lng * K), y: Math.round(ll.lat * K + WORLD) };
  }

  const mapBounds = L.latLngBounds(
    L.latLng(-CRS_MAX, 0),
    L.latLng(0, CRS_MAX)
  );

  // ======================================================================
  //  2. СОЗДАНИЕ КАРТЫ
  // ======================================================================
  const map = L.map('map', {
    crs: L.CRS.Simple,
    minZoom: 2.4,
    maxZoom: 8,
    zoomSnap: 0.25,
    zoomDelta: 0.5,
    wheelPxPerZoomLevel: 100,
    attributionControl: false,
    maxBounds: mapBounds.pad(0.18),
    maxBoundsViscosity: 0.85
  });

  // Автоматическая адаптация minZoom под размер экрана, чтобы карта не улетала далеко назад
  function adjustMinZoom() {
    try {
      const fitZoom = map.getBoundsZoom(mapBounds);
      const optimalMinZoom = Math.max(2.2, Math.min(3.0, fitZoom - 0.35));
      map.setMinZoom(optimalMinZoom);
    } catch (_) {}
  }
  adjustMinZoom();
  map.fitBounds(mapBounds);
  window.addEventListener('resize', adjustMinZoom);

  // Уровни детализации (LOD) в зависимости от текущего зума
  function updateZoomTier() {
    const z = map.getZoom();
    const mapEl = document.getElementById('map');
    if (!mapEl) return;

    mapEl.classList.remove('zoom-tier-far', 'zoom-tier-mid', 'zoom-tier-close');
    if (z < 3.8) {
      mapEl.classList.add('zoom-tier-far');
    } else if (z < 5.0) {
      mapEl.classList.add('zoom-tier-mid');
    } else {
      mapEl.classList.add('zoom-tier-close');
    }
  }

  map.on('zoom zoomend', updateZoomTier);
  updateZoomTier();

  // Топографическая карта Altis: здания, дороги, высоты, леса и береговая линия
  const topoLayer = L.tileLayer('', {
    tileSize: 256,
    minZoom: 2,
    maxZoom: 8,
    maxNativeZoom: 7,
    noWrap: true,
    bounds: mapBounds
  });
  topoLayer.getTileUrl = (coords) => {
    if (coords.z < 4) return `/topo-tiles/overview/${coords.z}/${coords.x}/${coords.y}.jpg`;
    return `/topo-tiles/${coords.z + 8}/map_${coords.x}_${coords.y}.jpg`;
  };
  // Кастомная широкая река из PBO: прозрачный оверлей поверх топографической карты.
  const riverBounds = L.latLngBounds(
    gameToLatLng(12000, 14880),
    gameToLatLng(15360, 23520)
  );
  const riverOverlay = L.imageOverlay('/river-overlay.webp', riverBounds, {
    opacity: 0.95,
    interactive: false,
    zIndex: 10
  });

  // Цветная спутниковая карта высокого разрешения со зданиями, дорогами и кастомной рекой
  const satelliteLayer = L.tileLayer('', {
    tileSize: 256,
    minZoom: 2,
    maxZoom: 8,
    maxNativeZoom: 7,
    noWrap: true,
    bounds: mapBounds
  });
  satelliteLayer.getTileUrl = (coords) => {
    if (coords.z < 4) return `/hybrid-tiles/overview/${coords.z}/${coords.x}/${coords.y}.jpg`;
    return `/hybrid-tiles/${coords.z + 8}/map_${coords.x}_${coords.y}.jpg`;
  };

  // По умолчанию активен цветной гибридный спутник (или выбор из localStorage)
  const savedBasemap = localStorage.getItem('altis_basemap_mode');
  let satelliteMode = (savedBasemap !== 'topo');
  const basemapButton = document.getElementById('btn-toggle-basemap');

  if (satelliteMode) {
    satelliteLayer.addTo(map);
    if (basemapButton) {
      basemapButton.textContent = 'ТОПО';
      basemapButton.classList.add('active');
    }
  } else {
    topoLayer.addTo(map);
    riverOverlay.addTo(map);
    if (basemapButton) {
      basemapButton.textContent = 'СПУТНИК';
      basemapButton.classList.remove('active');
    }
  }

  basemapButton?.addEventListener('click', () => {
    satelliteMode = !satelliteMode;
    localStorage.setItem('altis_basemap_mode', satelliteMode ? 'satellite' : 'topo');
    if (satelliteMode) {
      map.removeLayer(topoLayer);
      map.removeLayer(riverOverlay);
      satelliteLayer.addTo(map);
      basemapButton.textContent = 'ТОПО';
      basemapButton.classList.add('active');
    } else {
      map.removeLayer(satelliteLayer);
      topoLayer.addTo(map);
      riverOverlay.addTo(map);
      basemapButton.textContent = 'СПУТНИК';
      basemapButton.classList.remove('active');
    }
  });

  // ======================================================================
  //  3. КООРДИНАТНАЯ СЕТКА ARMA 3 (HUD И ОВЕРЛЕЙ)
  // ======================================================================
  const gridCoordEl = document.getElementById('grid-coord');
  const posCoordEl  = document.getElementById('pos-coord');

  map.on('mousemove', (e) => {
    const g = latLngToGame(e.latlng);
    const gx = Math.max(0, Math.min(WORLD, g.x));
    const gy = Math.max(0, Math.min(WORLD, g.y));

    const gridX = String(Math.floor(gx / 100)).padStart(3, '0');
    const gridY = String(Math.floor(gy / 100)).padStart(3, '0');

    gridCoordEl.textContent = `${gridX} ${gridY}`;
    posCoordEl.textContent  = `X: ${String(gx).padStart(5, ' ')} | Y: ${String(gy).padStart(5, ' ')}`;
  });

  const gridLayer = L.layerGroup();
  function redrawArmaGrid() {
    gridLayer.clearLayers();
    const bounds = map.getBounds();
    const sw = latLngToGame(bounds.getSouthWest());
    const ne = latLngToGame(bounds.getNorthEast());

    const minX = Math.max(0, Math.floor(sw.x / 1000) * 1000);
    const maxX = Math.min(WORLD, Math.ceil(ne.x / 1000) * 1000);
    const minY = Math.max(0, Math.floor(sw.y / 1000) * 1000);
    const maxY = Math.min(WORLD, Math.ceil(ne.y / 1000) * 1000);

    for (let x = minX; x <= maxX; x += 1000) {
      gridLayer.addLayer(L.polyline(
        [gameToLatLng(x, minY), gameToLatLng(x, maxY)],
        { color: 'rgba(255,255,255,0.3)', weight: 1, interactive: false }
      ));
    }
    for (let y = minY; y <= maxY; y += 1000) {
      gridLayer.addLayer(L.polyline(
        [gameToLatLng(minX, y), gameToLatLng(maxX, y)],
        { color: 'rgba(255,255,255,0.3)', weight: 1, interactive: false }
      ));
    }
  }
  map.on('moveend zoomend', redrawArmaGrid);
  redrawArmaGrid();

  /*
   * ВЕКТОРНАЯ ДОРОЖНАЯ СЕТЬ ИЗ КАСТОМНОЙ PBO.
   * Временно выключена: готовая топографическая подложка содержит свою сеть
   * дорог, а обе сети не совпадают. Код сохранён для будущей отдельной
   * подложки, построенной из той же PBO.
   *
  const roadsLayer = L.layerGroup();
  fetch('/api/roads')
    .then(r => r.json())
    .then(roads => roads.forEach(rd => {
      const latlngs = rd.pts.map(pt => gameToLatLng(pt[0], pt[1]));
      if (rd.type === 1) {
        roadsLayer.addLayer(L.polyline(latlngs, { className: 'road-highway-casing', interactive: false }));
        roadsLayer.addLayer(L.polyline(latlngs, { className: 'road-highway-core', interactive: false }));
      } else if (rd.type === 2) {
        roadsLayer.addLayer(L.polyline(latlngs, { className: 'road-main-casing', interactive: false }));
        roadsLayer.addLayer(L.polyline(latlngs, { className: 'road-main-core', interactive: false }));
      } else if (rd.type === 4) roadsLayer.addLayer(L.polyline(latlngs, { className: 'road-city', interactive: false }));
      else if (rd.type === 3) roadsLayer.addLayer(L.polyline(latlngs, { className: 'road-dirt', interactive: false }));
      else if (rd.type === 5) roadsLayer.addLayer(L.polyline(latlngs, { className: 'road-path', interactive: false }));
    }));
  */

  // ======================================================================
  //  5. ИНТЕРАКТИВНЫЕ ГАРАЖИ МИССИИ (КЛИКАБЕЛЬНЫЕ, СИСТЕМА ЗАХВАТА И ПАРОЛЕЙ)
  // ======================================================================
  const garagesLayer = L.layerGroup().addTo(map);
  const buildingPolygons = {};
  let selectedBuilding = null;

  function rotatedBox(gx, gy, w, h, dirDeg) {
    const rad = (dirDeg * Math.PI) / 180;
    const cos = Math.cos(rad);
    const sin = Math.sin(rad);
    const hw  = w / 2;
    const hh  = h / 2;

    return [[-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]].map(([cx, cy]) => {
      const rx = cx * cos + cy * sin;
      const ry = -cx * sin + cy * cos;
      return gameToLatLng(gx + rx, gy + ry);
    });
  }

  fetch('/api/buildings')
    .then(r => r.json())
    .then(garages => {
      garages.forEach(g => {
        // Навесы миссии не являются гаражами для захвата и не показываются на карте.
        if (g.class === 'Land_GarageShelter_01_F') return;

        // Увеличенные размеры квадратиков (16х18м) для отличной видимости и кликабельности
        const coords = rotatedBox(g.x, g.y, g.w || 16, g.l || 18, g.dir || g.yaw || 0);
        const isMission = (g.source === 'mission');

        const poly = L.polygon(coords, {
          className: isMission ? 'garage-polygon garage-mission' : 'garage-polygon',
          weight: 4,
          color: isMission ? '#fbbf24' : '#00f0ff',
          fillColor: isMission ? '#fbbf24' : '#00f0ff',
          fillOpacity: 0.88
        });

        poly._bData = g;
        poly.on('click', () => openBuildingPanel(g));

        poly.bindTooltip(() => {
          const c = claimsData[g.id];
          const typeBadge = isMission
            ? '<span style="color:#fbbf24; font-weight:bold;">★ Кастомный (миссия)</span>'
            : '<span style="color:#00f0ff; font-weight:bold;">🏛️ Островной</span>';

          if (c && (c.owner || c.status)) {
            const statusLabel = c.status === 'hostile'
              ? '<span style="color:#f85149; font-weight:bold;">🔴 Вражеский</span>'
              : c.status === 'ally'
              ? '<span style="color:#bc8cff; font-weight:bold;">🟣 Гараж друга</span>'
              : c.status === 'loot'
              ? '<span style="color:#d29922; font-weight:bold;">🟡 Склад</span>'
              : c.status === 'neutral'
              ? '<span style="color:#8b949e; font-weight:bold;">⚪ Свободный</span>'
              : '<span style="color:#3fb950; font-weight:bold;">🟢 Наш гараж</span>';

            return `<b>${g.name || 'Гараж'}</b><br>${typeBadge} • ${statusLabel}<br>Владелец: <span style="color:#58a6ff">${c.owner || '—'}</span><br>Пароль: <code>${c.password ? '••••••' : 'Нет'}</code>`;
          }
          return `<b>${g.name || 'Гараж'}</b><br>${typeBadge}<br><small style="color:#58a6ff">Клик — задать владельца и пароль</small>`;
        }, { className: 'tactical-tooltip', sticky: true });

        garagesLayer.addLayer(poly);
        buildingPolygons[g.id] = poly;
      });
      updateBuildingsVisuals();
    });

  function updateBuildingsVisuals() {
    Object.keys(buildingPolygons).forEach(updateBuildingVisual);
  }

  function updateBuildingVisual(id) {
    const poly = buildingPolygons[id];
    if (!poly) return;
    const c = claimsData[id];
    const g = poly._bData;
    const el = poly.getElement();

    if (el) {
      el.classList.remove('status-friendly', 'status-ally', 'status-hostile', 'status-loot', 'status-neutral');
    }

    const isMission = (g && g.source === 'mission');
    const defaultCol = isMission ? '#fbbf24' : '#00f0ff';

    if (!c || (!c.owner && !c.status)) {
      poly.setStyle({
        color: defaultCol,
        fillColor: defaultCol,
        fillOpacity: 0.88,
        weight: 4
      });
      return;
    }

    const palette = {
      friendly: '#3fb950',
      ally: '#bc8cff',
      hostile: '#f85149',
      loot: '#d29922',
      neutral: '#8b949e'
    };
    const col = palette[c.status] || palette.friendly;
    poly.setStyle({
      color: col,
      fillColor: col,
      fillOpacity: 0.88,
      weight: 4
    });

    if (el) {
      el.classList.add(`status-${c.status || 'friendly'}`);
    }
  }

  // ======================================================================
  //  6. СЛОИ КАТЕГОРИЙ И НАЗВАНИЯ ГОРОДОВ (ТОЧНЫЙ ЦВЕТ И ШРИФТ ARMA 3)
  // ======================================================================
  const categoryLayers = {
    names: L.layerGroup().addTo(map),
    resources: L.layerGroup().addTo(map),
    routes: L.layerGroup().addTo(map),
    shops: L.layerGroup().addTo(map),
    infra: L.layerGroup().addTo(map),
    // Метки категории «Недвижимость». Интерактивные гаражи живут отдельно
    // в garagesLayer и всегда остаются на карте.
    realestate: L.layerGroup().addTo(map),
    dp: L.layerGroup().addTo(map),
    bases: L.layerGroup().addTo(map),
    illegal: L.layerGroup().addTo(map),
    other: L.layerGroup().addTo(map),
    territories: L.layerGroup().addTo(map)
  };
  function cleanMarkerLabel(value) {
    return String(value || '')
      .replace(/^\s*amazingrp(?:g)?\.ru\s*\|\s*/i, '')
      .trim();
  }

  let allSettlementsData = [];
  let allDPMarkersData = [];

  function getGarageLandmark(x, y) {
    let nearestCity = null;
    let minCityDist = Infinity;
    if (allSettlementsData && allSettlementsData.length) {
      for (let i = 0; i < allSettlementsData.length; i++) {
        const c = allSettlementsData[i];
        const d = Math.hypot(c.x - x, c.y - y);
        if (d < minCityDist) {
          minCityDist = d;
          nearestCity = c;
        }
      }
    }

    let nearestDP = null;
    let minDPDist = Infinity;
    if (allDPMarkersData && allDPMarkersData.length) {
      for (let i = 0; i < allDPMarkersData.length; i++) {
        const dp = allDPMarkersData[i];
        const d = Math.hypot(dp.x - x, dp.y - y);
        if (d < minDPDist) {
          minDPDist = d;
          nearestDP = dp;
        }
      }
    }

    const fmt = (d) => {
      if (isNaN(d) || d === Infinity) return '';
      return d < 1000 ? `~${Math.round(d)}м` : `~${(d / 1000).toFixed(1)}км`;
    };

    // Если гараж дальше 700 метров от DP, НЕ привязываем к DP (только деревня/город)
    const hasNearbyDP = (minDPDist <= 700 && nearestDP);
    const dpLabel = hasNearbyDP ? (cleanMarkerLabel(nearestDP.text) || (nearestDP.name || '').toUpperCase()) : '';

    return {
      cityName: nearestCity ? nearestCity.name : '',
      cityDist: minCityDist,
      cityFormattedDist: fmt(minCityDist),
      dpName: dpLabel,
      dpDist: hasNearbyDP ? minDPDist : Infinity,
      dpFormattedDist: hasNearbyDP ? fmt(minDPDist) : ''
    };
  }

  const citiesLayer = categoryLayers.names;

  fetch('/api/cities')
    .then(r => r.json())
    .then(cities => {
      const isNamedPlace = c => {
        if (['NameCityCapital', 'NameCity', 'NameVillage'].includes(c.type)) return true;
        if (c.type === 'NameLocal') {
          if (/^(factory|military|quarry|dump|airbase|terminal|storage|mine|power plant)/i.test(c.name)) return false;
          if (['castle', 'dump'].includes((c.name || '').toLowerCase())) return false;
          return true;
        }
        return false;
      };
      allSettlementsData = cities.filter(isNamedPlace);
      if (!allSettlementsData.length) allSettlementsData = cities;
      renderClaimsTable();
      cities.forEach(c => {
        let cls = 'arma-city-village';
        let labelText = c.name;

        if (c.type === 'NameCityCapital') {
          cls = 'arma-city-capital';
          labelText = c.name.toUpperCase();
        } else if (c.type === 'NameCity' || c.type === 'CityCenter') {
          cls = 'arma-city-normal';
        } else if (c.type === 'NameVillage') {
          cls = 'arma-city-village';
        } else if (c.type === 'NameMarine') {
          cls = 'arma-city-marine';
          labelText = c.name.toLowerCase();
        } else if (c.type === 'Hill') {
          cls = 'arma-city-hill';
          labelText = c.name ? `▲ ${c.name}` : `▲ ${(Math.round(c.y % 350 + 80))}m`;
        } else if (c.type === 'NameLocal') {
          cls = 'arma-city-local';
          labelText = c.name.replace(/\d+$/, '').toLowerCase();
        }

        const icon = L.divIcon({
          className: `arma-city-label ${cls}`,
          html: labelText,
          iconSize: [160, 20],
          iconAnchor: [80, 10]
        });

        const marker = L.marker(gameToLatLng(c.x, c.y), { icon, interactive: false });
        categoryLayers.names.addLayer(marker);
      });
    });

  // ======================================================================
  //  7. ИКОНКИ МИССИИ ПО 11 КАТЕГОРИЯМ (ОРИГИНАЛЬНЫЕ PNG ИЗ AMAZING_MARKERS)
  // ======================================================================
  const allMarkerEntries = []; // { marker, data, cat }

  fetch('/api/markers')
    .then(r => r.json())
    .then(markers => {
      allDPMarkersData = markers.filter(m => m.category === 'dp' || (m.name && m.name.toLowerCase().startsWith('dp_')) || (m.text && /dp\s*\d+/i.test(m.text)));
      renderClaimsTable();
      markers.forEach(m => {
        const isDP = (m.category === 'dp');
        const label = cleanMarkerLabel(m.text);
        let iconInner = '';

        if (m.icon) {
          iconInner = `<img src="${m.icon}" class="arma-marker-img" />`;
        } else if (m.name.toLowerCase().includes('atm') || m.type === 'atm') {
          iconInner = `<img src="/icons/atm.png" class="arma-marker-img" />`;
        } else if (m.type === 'loc_Fountain' || m.name === 'marker_286') {
          iconInner = `<img src="/icons/loc_Fountain.png" class="arma-marker-img" />`;
        } else {
          iconInner = `<span class="arma-marker-icon">📍</span>`;
        }

        const iconWrapClass = isDP ? 'arma-marker-wrap arma-marker-dp' : 'arma-marker-wrap';
        const icon = L.divIcon({
          className: iconWrapClass,
          html: `${iconInner}<span class="arma-marker-text">${label}</span>`,
          iconSize: null,
          iconAnchor: [14, 14]
        });

        const marker = L.marker(gameToLatLng(m.x, m.y), { icon });
        marker.bindTooltip(`<b>${label}</b><br><small style="color:#8b949e">Категория: ${m.category}<br>X: ${m.x} | Y: ${m.y}</small>`, {
          className: 'tactical-tooltip',
          offset: [0, -12]
        });

        const targetCat = m.category || 'other';
        const targetLayer = categoryLayers[targetCat] || categoryLayers.other;
        targetLayer.addLayer(marker);

        allMarkerEntries.push({ marker, data: m, cat: targetCat });
      });
    });

  // ======================================================================
  //  7.1 ТЕРРИТОРИИ И ЗОНЫ (СЕЙФЗОНЫ, УРАН, ОХОТА)
  // ======================================================================
  function createEllipsePolygon(gx, gy, rx, ry, angleDeg, numPoints = 36) {
    const pts = [];
    const radAngle = (angleDeg * Math.PI) / 180;
    const cosA = Math.cos(radAngle);
    const sinA = Math.sin(radAngle);
    for (let i = 0; i < numPoints; i++) {
      const theta = (i * 2 * Math.PI) / numPoints;
      const dx = rx * Math.cos(theta);
      const dy = ry * Math.sin(theta);
      const rxRot = dx * cosA + dy * sinA;
      const ryRot = -dx * sinA + dy * cosA;
      pts.push(gameToLatLng(gx + rxRot, gy + ryRot));
    }
    return pts;
  }

  function createRectanglePolygon(gx, gy, rx, ry, angleDeg) {
    const radAngle = (angleDeg * Math.PI) / 180;
    const cosA = Math.cos(radAngle);
    const sinA = Math.sin(radAngle);
    const corners = [
      [-rx, -ry], [rx, -ry], [rx, ry], [-rx, ry]
    ];
    return corners.map(([cx, cy]) => {
      const rxRot = cx * cosA + cy * sinA;
      const ryRot = -cx * sinA + cy * cosA;
      return gameToLatLng(gx + rxRot, gy + ryRot);
    });
  }

  let territoriesList = [];
  const territoryBounds = L.latLngBounds();

  fetch('/api/territories')
    .then(r => r.json())
    .then(zones => {
      territoriesList = zones;
      zones.forEach(z => {
        let pts;
        if (z.shape === 'rectangle') {
          pts = createRectanglePolygon(z.x, z.y, z.radius_x, z.radius_y, z.angle || 0);
        } else {
          pts = createEllipsePolygon(z.x, z.y, z.radius_x, z.radius_y, z.angle || 0);
        }

        const poly = L.polygon(pts, {
          color: z.color || '#22c55e',
          fillColor: z.color || '#22c55e',
          fillOpacity: 0.22,
          weight: 2,
          dashArray: '6, 6'
        });

        poly.bindTooltip(`<b>${z.label}</b><br><small style="color:#8b949e">Радиус: ${z.radius_x}м | X: ${z.x} Y: ${z.y}</small>`, {
          className: 'tactical-tooltip',
          sticky: true
        });

        categoryLayers.territories.addLayer(poly);
        territoryBounds.extend(poly.getBounds());

        // Подпись по центру зоны
        const centerMarker = L.marker(gameToLatLng(z.x, z.y), {
          icon: L.divIcon({
            className: 'arma-zone-label',
            html: `<span>${z.label}</span>`,
            iconSize: [220, 24],
            iconAnchor: [110, 12]
          }),
          interactive: false
        });
        categoryLayers.territories.addLayer(centerMarker);
      });
      renderTerritoriesModal();
    });

  // ======================================================================
  //  8. АВТОРИЗАЦИЯ, SOCKET.IO И СИСТЕМА СКВАДОВ
  // ======================================================================
  const socket = io();
  let currentUser = null;
  let authToken   = localStorage.getItem('arma_token') || null;
  let claimsData  = {};
  let currentSquadData = null;
  let currentOnlineIds = new Set();

  // Инициализация авторизации при загрузке
  async function initAuth() {
    checkServerConfig();
    if (!authToken) {
      updateAuthUI();
      handleInviteParam();
      return;
    }
    try {
      const res = await fetch('/api/auth/me', {
        headers: { 'Authorization': 'Bearer ' + authToken }
      });
      if (res.ok) {
        const data = await res.json();
        currentUser = data.user;
        socket.emit('auth_socket', { token: authToken });
      } else {
        authToken = null;
        localStorage.removeItem('arma_token');
      }
    } catch (e) {
      console.warn('Сервер недоступен для проверки сессии:', e);
    }
    updateAuthUI();
    handleInviteParam();
  }

  async function checkServerConfig() {
    try {
      const res = await fetch('/api/config');
      const data = await res.json();
      if (data.googleClientId && window.google) {
        document.getElementById('google-auth-container')?.classList.remove('hidden');
        document.getElementById('google-not-configured-notice')?.classList.add('hidden');
        google.accounts.id.initialize({
          client_id: data.googleClientId,
          callback: window.handleGoogleCredentialResponse
        });
        const slot = document.getElementById('google-button-slot');
        if (slot) {
          google.accounts.id.renderButton(slot, {
            theme: 'filled_blue',
            size: 'large',
            text: 'signin_with',
            shape: 'rectangular'
          });
        }
      }
    } catch (e) {
      console.warn('Config fetch error:', e);
    }
  }

  function updateAuthUI() {
    const btnAuth = document.getElementById('btn-open-auth-modal');
    const badge = document.getElementById('user-profile-badge');
    const avatarImg = document.getElementById('user-avatar-img');
    const nameEl = document.getElementById('user-display-name');
    const squadNameEl = document.getElementById('current-squad-name');
    const soloView = document.getElementById('squad-solo-view');
    const activeView = document.getElementById('squad-active-view');

    if (currentUser) {
      btnAuth?.classList.add('hidden');
      badge?.classList.remove('hidden');
      if (avatarImg) avatarImg.src = currentUser.avatar || ('https://api.dicebear.com/7.x/bottts/svg?seed=' + currentUser.id);
      if (nameEl) nameEl.textContent = currentUser.name || currentUser.username || 'Боец';

      if (currentUser.squadId) {
        squadNameEl.textContent = currentUser.squadId;
        squadNameEl.className = 'hud-squad-badge squad-active';
        soloView?.classList.add('hidden');
        activeView?.classList.remove('hidden');
        const actName = document.getElementById('active-squad-name');
        if (actName) actName.textContent = currentUser.squadId;
      } else {
        squadNameEl.textContent = 'ОДИНОЧКА';
        squadNameEl.className = 'hud-squad-badge';
        soloView?.classList.remove('hidden');
        activeView?.classList.add('hidden');
      }

      // Если была отложенная заявка по ссылке-приглашению
      const pendingSquad = sessionStorage.getItem('pending_join_squad');
      if (pendingSquad) {
        sessionStorage.removeItem('pending_join_squad');
        if (currentUser.squadId !== pendingSquad) {
          setTimeout(() => {
            if (confirm(`Вы авторизовались! Отправить заявку на вступление в сквад "${pendingSquad}" командиру?`)) {
              requestJoinSquad(pendingSquad);
            }
          }, 300);
        }
      }
    } else {
      btnAuth?.classList.remove('hidden');
      badge?.classList.add('hidden');
      squadNameEl.textContent = 'ГОСТЬ';
      squadNameEl.className = 'hud-squad-badge';
      soloView?.classList.remove('hidden');
      activeView?.classList.add('hidden');
    }
  }

  // Google One Tap / GIS callback
  window.handleGoogleCredentialResponse = async (response) => {
    try {
      const res = await fetch('/api/auth/google', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: response.credential })
      });
      const data = await res.json();
      if (res.ok && data.token) {
        authToken = data.token;
        currentUser = data.user;
        localStorage.setItem('arma_token', authToken);
        updateAuthUI();
        document.getElementById('auth-modal')?.classList.add('hidden');
        socket.emit('auth_socket', { token: authToken });
      } else {
        showAuthMsg(data.error || 'Ошибка входа Google', 'error');
      }
    } catch (e) {
      showAuthMsg('Ошибка соединения с сервером', 'error');
    }
  };

  function showAuthMsg(msg, type) {
    const el = document.getElementById('auth-status-msg');
    if (!el) return;
    el.textContent = msg;
    el.className = 'auth-status-msg ' + (type || '');
    el.classList.remove('hidden');
  }

  // Socket.io события
  socket.on('connect', () => {
    if (authToken) socket.emit('auth_socket', { token: authToken });
  });

  socket.on('squad_data', (squad) => {
    currentSquadData = squad;
    claimsData = squad.claims || {};
    updateBuildingsVisuals();
    renderClaimsTable();
    renderSquadMembers(squad.members || []);
  });

  socket.on('personal_data', (personalGarages) => {
    currentSquadData = null;
    claimsData = personalGarages || {};
    updateBuildingsVisuals();
    renderClaimsTable();
  });

  socket.on('squad_members_updated', (members) => {
    if (currentSquadData) currentSquadData.members = members;
    renderSquadMembers(members);
  });

  socket.on('squad_online', (onlineIds) => {
    currentOnlineIds = new Set(onlineIds);
    if (currentSquadData && currentSquadData.members) {
      renderSquadMembers(currentSquadData.members);
    }
  });

  socket.on('user_kicked_event', ({ userId, squadName }) => {
    if (currentUser && currentUser.id === userId) {
      alert('Вы были исключены из сквада командиром.');
      currentUser.squadId = null;
      claimsData = currentUser.personalGarages || {};
      updateBuildingsVisuals();
      renderClaimsTable();
      updateAuthUI();
      socket.emit('auth_socket', { token: authToken });
    }
  });

  socket.on('squad_disbanded', ({ squadName }) => {
    if (currentUser && currentUser.squadId === squadName) {
      alert(`Сквад "${squadName}" был распущен командиром.`);
      currentUser.squadId = null;
      currentSquadData = null;
      claimsData = currentUser.personalGarages || {};
      updateBuildingsVisuals();
      renderClaimsTable();
      updateAuthUI();
      squadModal.classList.add('hidden');
      socket.emit('auth_socket', { token: authToken });
    }
  });

  socket.on('squad_requests_updated', (requests) => {
    if (currentSquadData) currentSquadData.joinRequests = requests;
    renderSquadRequests(requests);
  });

  socket.on('user_request_accepted_event', ({ userId, squadName }) => {
    if (currentUser && currentUser.id === userId) {
      alert(`🎉 Ваша заявка в сквад "${squadName}" принята командиром! Добро пожаловать в отряд.`);
      currentUser.squadId = squadName;
      updateAuthUI();
      socket.emit('auth_socket', { token: authToken });
    }
  });

  socket.on('user_request_rejected_event', ({ userId, squadName }) => {
    if (currentUser && currentUser.id === userId) {
      alert(`Командир сквада "${squadName}" отклонил вашу заявку на вступление.`);
    }
  });

  socket.on('claim_updated', (c) => {
    claimsData[c.id] = c;
    updateBuildingVisual(c.id);
    renderClaimsTable();
  });

  socket.on('claim_removed', (id) => {
    delete claimsData[id];
    updateBuildingVisual(id);
    renderClaimsTable();
  });

  socket.on('squad_claims_all_updated', (claims) => {
    claimsData = claims || {};
    updateBuildingsVisuals();
    renderClaimsTable();
  });

  function renderSquadMembers(members) {
    const ul = document.getElementById('squad-members-list');
    if (!ul) return;
    ul.innerHTML = '';
    if (!members || members.length === 0) {
      ul.innerHTML = '<li class="empty-list">Нет участников</li>';
      return;
    }

    const myMember = currentSquadData?.members?.find(m => m.userId === currentUser?.id);
    const isLeader = currentUser && currentSquadData && (currentSquadData.leaderId === currentUser.id || myMember?.role === 'leader');
    const isAdmin = myMember?.role === 'admin';
    const canManageAdmin = isLeader || isAdmin;

    const roleBadge = document.getElementById('active-user-role');
    if (roleBadge) {
      if (isLeader) {
        roleBadge.textContent = 'Командир';
        roleBadge.style.borderColor = '#eab308';
        roleBadge.style.color = '#fde047';
      } else if (isAdmin) {
        roleBadge.textContent = 'Админ';
        roleBadge.style.borderColor = '#a855f7';
        roleBadge.style.color = '#c084fc';
      } else {
        roleBadge.textContent = 'Боец';
        roleBadge.style.borderColor = '#3b82f6';
        roleBadge.style.color = '#93c5fd';
      }
    }

    const leaderPanel = document.getElementById('leader-control-panel');
    const disbandBtn = document.getElementById('btn-disband-squad');
    if (disbandBtn) {
      if (isLeader) disbandBtn.classList.remove('hidden');
      else disbandBtn.classList.add('hidden');
    }

    // Панель управления (ссылка, заявки, массовая смена паролей) доступна Лидеру и Админам
    if (leaderPanel) {
      if (canManageAdmin) {
        leaderPanel.classList.remove('hidden');
        const passIn = document.getElementById('squad-passcode-input');
        if (passIn && currentSquadData.passcode) passIn.value = currentSquadData.passcode;
        const linkIn = document.getElementById('squad-invite-link-input');
        if (linkIn && currentSquadData) {
          linkIn.value = window.location.origin + '/?join_squad=' + encodeURIComponent(currentSquadData.name);
        }
        renderSquadRequests(currentSquadData.joinRequests || []);
      } else {
        leaderPanel.classList.add('hidden');
      }
    }

    // В модалке Списка Гаражей скрываем быструю смену паролей для обычных бойцов
    const bulkQuickWrap = document.getElementById('bulk-garage-password-wrap-quick');
    if (bulkQuickWrap) {
      if (!currentUser?.squadId || canManageAdmin) {
        bulkQuickWrap.classList.remove('hidden');
      } else {
        bulkQuickWrap.classList.add('hidden');
      }
    }

    members.forEach(m => {
      const li = document.createElement('li');
      li.className = 'member-item';

      const isOnline = currentOnlineIds.has(m.userId);
      const isMemberLeader = currentSquadData && (currentSquadData.leaderId === m.userId || m.role === 'leader');
      const isMemberAdmin = !isMemberLeader && m.role === 'admin';

      const roleBadgeHtml = isMemberLeader 
        ? '<span class="member-role-badge role-leader">👑 Командир</span>' 
        : isMemberAdmin 
        ? '<span class="member-role-badge role-admin">🛡️ Админ</span>' 
        : '<span class="member-role-badge role-member">👤 Боец</span>';

      li.innerHTML = `
        <div class="member-info-col">
          <span class="member-status-dot ${isOnline ? 'online' : ''}" title="${isOnline ? 'В сети' : 'Не в сети'}"></span>
          <img src="${m.avatar || ('https://api.dicebear.com/7.x/bottts/svg?seed=' + m.userId)}" class="member-avatar" alt="">
          <span class="member-name">${m.name || 'Боец'}</span>
          ${roleBadgeHtml}
        </div>
        <div class="member-actions"></div>
      `;

      const actionsCol = li.querySelector('.member-actions');

      // Кнопки управления участником — ТОЛЬКО ДЛЯ КОМАНДИРА (ЛИДЕРА)
      if (isLeader && m.userId !== currentUser.id) {
        // Кнопка повышения / понижения роли
        const roleBtn = document.createElement('button');
        if (isMemberAdmin) {
          roleBtn.className = 'btn-role-demote';
          roleBtn.textContent = '⬇ СНЯТЬ АДМИНА';
          roleBtn.title = 'Понизить до обычного бойца';
          roleBtn.onclick = async () => {
            if (!confirm(`Снять статус администратора с "${m.name}"?`)) return;
            await changeMemberRole(m.userId, 'member');
          };
        } else {
          roleBtn.className = 'btn-role-promote';
          roleBtn.textContent = '⬆ В АДМИНЫ';
          roleBtn.title = 'Назначить администратором сквада';
          roleBtn.onclick = async () => {
            if (!confirm(`Повысить бойца "${m.name}" до Администратора сквада?`)) return;
            await changeMemberRole(m.userId, 'admin');
          };
        }
        actionsCol.appendChild(roleBtn);

        // Кнопка кика
        const kickBtn = document.createElement('button');
        kickBtn.className = 'btn-kick-member';
        kickBtn.textContent = 'КИКНУТЬ';
        kickBtn.onclick = async () => {
          if (!confirm(`Выгнать бойца "${m.name}" из сквада?`)) return;
          try {
            const res = await fetch('/api/squads/kick', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + authToken
              },
              body: JSON.stringify({ targetUserId: m.userId })
            });
            const data = await res.json();
            if (!res.ok) alert(data.error || 'Ошибка при исключении');
          } catch (e) {
            alert('Ошибка сети');
          }
        };
        actionsCol.appendChild(kickBtn);
      }

      ul.appendChild(li);
    });
  }

  async function changeMemberRole(targetUserId, newRole) {
    try {
      const res = await fetch('/api/squads/set_role', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + authToken
        },
        body: JSON.stringify({ targetUserId, newRole })
      });
      const data = await res.json();
      if (res.ok) {
        if (currentSquadData) {
          currentSquadData.members = data.members;
        }
        renderSquadMembers(data.members);
      } else {
        alert(data.error || 'Ошибка изменения роли');
      }
    } catch (e) {
      alert('Ошибка сети при изменении роли');
    }
  }

  function renderSquadRequests(requests) {
    const ul = document.getElementById('squad-requests-list');
    const countEl = document.getElementById('squad-requests-count');
    if (!ul) return;
    const reqs = requests || [];
    if (countEl) countEl.textContent = reqs.length;

    ul.innerHTML = '';
    if (reqs.length === 0) {
      ul.innerHTML = '<li class="empty-list" style="color:var(--text-muted); font-size:12px;">Нет новых заявок</li>';
      return;
    }

    reqs.forEach(r => {
      const li = document.createElement('li');
      li.className = 'request-item';
      li.innerHTML = `
        <div class="member-info-col">
          <img src="${r.avatar || ('https://api.dicebear.com/7.x/bottts/svg?seed=' + r.userId)}" class="member-avatar" alt="">
          <div>
            <div style="font-weight:600; font-size:13px; color:#f0f6fc;">${r.name || 'Боец'}</div>
            <div style="font-size:10px; color:#8b949e;">${r.requestedAt ? new Date(r.requestedAt).toLocaleTimeString() : ''}</div>
          </div>
        </div>
        <div class="request-actions">
          <button class="btn-accept-request">✓ ПРИНЯТЬ</button>
          <button class="btn-reject-request">✕</button>
        </div>
      `;

      li.querySelector('.btn-accept-request').onclick = () => acceptJoinRequest(r.userId);
      li.querySelector('.btn-reject-request').onclick = () => rejectJoinRequest(r.userId);

      ul.appendChild(li);
    });
  }

  async function acceptJoinRequest(targetUserId) {
    try {
      const res = await fetch('/api/squads/accept_request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + authToken
        },
        body: JSON.stringify({ targetUserId })
      });
      const data = await res.json();
      if (!res.ok) alert(data.error || 'Ошибка принятия заявки');
    } catch (e) {
      alert('Ошибка сети');
    }
  }

  async function rejectJoinRequest(targetUserId) {
    try {
      const res = await fetch('/api/squads/reject_request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + authToken
        },
        body: JSON.stringify({ targetUserId })
      });
      const data = await res.json();
      if (!res.ok) alert(data.error || 'Ошибка отклонения заявки');
    } catch (e) {
      alert('Ошибка сети');
    }
  }

  // Обработка перехода по ссылке-приглашению
  async function handleInviteParam() {
    const urlParams = new URLSearchParams(window.location.search);
    const inviteSquad = urlParams.get('join_squad');
    if (!inviteSquad) return;

    window.history.replaceState({}, document.title, window.location.pathname);

    if (!currentUser) {
      sessionStorage.setItem('pending_join_squad', inviteSquad);
      alert(`Вы перешли по приглашению в сквад "${inviteSquad}".\nПожалуйста, войдите в аккаунт или зарегистрируйтесь, чтобы отправить заявку командиру.`);
      const am = document.getElementById('auth-modal');
      if (am) am.classList.remove('hidden');
      return;
    }

    if (currentUser.squadId === inviteSquad) {
      alert(`Вы уже состоите в скваде "${inviteSquad}".`);
      return;
    }

    const confirmMsg = currentUser.squadId
      ? `Вы перешли по приглашению в сквад "${inviteSquad}".\nСейчас вы состоите в "${currentUser.squadId}".\nОтправить заявку командиру "${inviteSquad}"?`
      : `Отправить заявку на вступление в сквад "${inviteSquad}" командиру отряда?`;

    if (confirm(confirmMsg)) {
      requestJoinSquad(inviteSquad);
    }
  }

  async function requestJoinSquad(squadName) {
    try {
      const res = await fetch('/api/squads/request_join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + authToken
        },
        body: JSON.stringify({ squadName })
      });
      const data = await res.json();
      if (res.ok) {
        alert(data.message || `Заявка в сквад "${squadName}" успешно отправлена командиру!`);
      } else {
        alert(data.error || 'Ошибка отправки заявки');
      }
    } catch (e) {
      alert('Ошибка сети при отправке заявки');
    }
  }

  // Копирование ссылки-приглашения
  document.getElementById('btn-copy-squad-invite')?.addEventListener('click', () => {
    const linkIn = document.getElementById('squad-invite-link-input');
    if (!linkIn || !linkIn.value) return;
    navigator.clipboard.writeText(linkIn.value).then(() => {
      const btn = document.getElementById('btn-copy-squad-invite');
      const oldText = btn.textContent;
      btn.textContent = '✓ СКОПИРОВАНО!';
      btn.style.color = '#3fb950';
      setTimeout(() => {
        btn.textContent = oldText;
        btn.style.color = '';
      }, 2000);
    }).catch(() => {
      alert('Ссылка: ' + linkIn.value);
    });
  });

  // ======================================================================
  //  9. БОКОВАЯ ПАНЕЛЬ ПОСТРОЙКИ (ВЛАДЕЛЕЦ / ПАРОЛЬ)
  // ======================================================================
  const panel       = document.getElementById('building-panel');
  const panelName   = document.getElementById('panel-building-name');
  const panelId     = document.getElementById('panel-building-id');
  const panelCoords = document.getElementById('panel-building-coords');
  const ownerIn     = document.getElementById('claim-owner');
  const passIn      = document.getElementById('claim-password');
  const statusIn    = document.getElementById('claim-status');
  const notesIn     = document.getElementById('claim-notes');
  const btnSaveClaim = document.getElementById('btn-save-claim');

  function openBuildingPanel(b) {
    selectedBuilding = b;
    panelName.textContent   = b.name || (b.type || '').replace(/^Land_/, '');
    panelId.textContent     = `ID: ${b.id}`;

    const lm = getGarageLandmark(b.x, b.y);
    const lmParts = [];
    if (lm.cityName) lmParts.push(`🏙️ ${lm.cityName} (${lm.cityFormattedDist})`);
    if (lm.dpName) lmParts.push(`📦 ${lm.dpName} (${lm.dpFormattedDist})`);
    const lmText = lmParts.join(' • ');
    panelCoords.innerHTML = `X: ${Math.round(b.x)}, Y: ${Math.round(b.y)}${lmText ? `<br><small style="color:#e3b341; font-weight:500;">${lmText}</small>` : ''}`;

    const c = claimsData[b.id] || {};
    ownerIn.value  = (c.owner !== undefined) ? c.owner : '';
    passIn.value   = c.password || '';
    statusIn.value = c.status   || 'friendly';
    notesIn.value  = c.notes    || '';

    if (btnSaveClaim) {
      if (currentUser && currentUser.squadId) {
        btnSaveClaim.textContent = 'СОХРАНИТЬ В СКВАД';
      } else {
        btnSaveClaim.textContent = 'СОХРАНИТЬ (ЛИЧНЫЙ)';
      }
    }

    panel.classList.remove('hidden');
  }

  document.getElementById('panel-close-btn').addEventListener('click', () => {
    panel.classList.add('hidden');
    selectedBuilding = null;
  });

  btnSaveClaim?.addEventListener('click', () => {
    if (!selectedBuilding) return;
    if (!currentUser) {
      alert('Пожалуйста, авторизуйтесь в правом верхнем углу, чтобы сохранять свои гаражи и пароли!');
      document.getElementById('auth-modal')?.classList.remove('hidden');
      return;
    }

    const obj = {
      id: selectedBuilding.id,
      type: selectedBuilding.type,
      x: selectedBuilding.x,
      y: selectedBuilding.y,
      owner: ownerIn.value.trim() || currentUser.name,
      password: passIn.value.trim(),
      status: statusIn.value,
      notes: notesIn.value.trim(),
      updatedBy: currentUser.name,
      updatedAt: new Date().toISOString()
    };

    socket.emit('save_claim', { claim: obj });
    claimsData[selectedBuilding.id] = obj;
    updateBuildingVisual(selectedBuilding.id);
    renderClaimsTable();
    panel.classList.add('hidden');
  });

  document.getElementById('btn-delete-claim').addEventListener('click', () => {
    if (!selectedBuilding) return;
    if (!currentUser) return;
    socket.emit('delete_claim', { claimId: selectedBuilding.id });
    delete claimsData[selectedBuilding.id];
    updateBuildingVisual(selectedBuilding.id);
    renderClaimsTable();
    panel.classList.add('hidden');
  });

  document.getElementById('btn-toggle-password-view').addEventListener('click', () => {
    passIn.type = passIn.type === 'password' ? 'text' : 'password';
  });

  document.getElementById('btn-copy-password').addEventListener('click', () => {
    if (!passIn.value) return;
    navigator.clipboard.writeText(passIn.value).then(() => {
      alert('Пароль скопирован в буфер обмена!');
    });
  });

  // ======================================================================
  //  10. МОДАЛКИ: АВТОРИЗАЦИЯ И СКВАДЫ (ОБРАБОТКА ФОРМ)
  // ======================================================================

  // Логин по паролю
  document.getElementById('btn-auth-login')?.addEventListener('click', async () => {
    const u = document.getElementById('auth-username').value.trim();
    const p = document.getElementById('auth-password').value.trim();
    if (!u || !p) return showAuthMsg('Заполните логин и пароль', 'error');

    showAuthMsg('Вход в систему...', '');

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p })
      });
      const data = await res.json();
      if (res.ok && data.token) {
        authToken = data.token;
        currentUser = data.user;
        localStorage.setItem('arma_token', authToken);
        updateAuthUI();
        authModal.classList.add('hidden');
        if (typeof socket !== 'undefined' && socket) {
          socket.emit('auth_socket', { token: authToken });
        }
      } else {
        showAuthMsg(data.error || 'Ошибка входа', 'error');
      }
    } catch (e) {
      showAuthMsg('Ошибка сети при входе', 'error');
    }
  });

  // Нажатие Enter в полях логина
  ['auth-username', 'auth-password'].forEach(id => {
    document.getElementById(id)?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        document.getElementById('btn-auth-login')?.click();
      }
    });
  });

  // Регистрация
  document.getElementById('btn-auth-register')?.addEventListener('click', async () => {
    const u = document.getElementById('auth-username').value.trim();
    const p = document.getElementById('auth-password').value.trim();
    const n = document.getElementById('auth-name').value.trim() || u;
    if (!u || !p) return showAuthMsg('Заполните логин и пароль', 'error');

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p, name: n })
      });
      const data = await res.json();
      if (res.ok && data.token) {
        authToken = data.token;
        currentUser = data.user;
        localStorage.setItem('arma_token', authToken);
        updateAuthUI();
        authModal.classList.add('hidden');
        socket.emit('auth_socket', { token: authToken });
      } else {
        showAuthMsg(data.error || 'Ошибка регистрации', 'error');
      }
    } catch (e) {
      showAuthMsg('Ошибка сети', 'error');
    }
  });

  // Выход из аккаунта
  document.getElementById('btn-logout')?.addEventListener('click', () => {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('arma_token');
    claimsData = {};
    updateBuildingsVisuals();
    renderClaimsTable();
    updateAuthUI();
    window.location.reload();
  });

  // Создание сквада
  document.getElementById('btn-create-squad')?.addEventListener('click', async () => {
    if (!currentUser) return;
    const n = document.getElementById('new-squad-name').value.trim();
    const p = document.getElementById('new-squad-password').value.trim();
    if (!n) return alert('Введите название сквада!');

    try {
      const res = await fetch('/api/squads/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + authToken
        },
        body: JSON.stringify({ name: n, passcode: p })
      });
      const data = await res.json();
      if (res.ok) {
        currentUser = data.user;
        squadModal.classList.add('hidden');
        updateAuthUI();
        socket.emit('auth_socket', { token: authToken });
      } else {
        alert(data.error || 'Ошибка создания сквада');
      }
    } catch (e) {
      alert('Ошибка сети');
    }
  });

  // Вступление в сквад
  document.getElementById('btn-join-squad')?.addEventListener('click', async () => {
    if (!currentUser) return;
    const n = document.getElementById('join-squad-name').value.trim();
    const p = document.getElementById('join-squad-password').value.trim();
    if (!n) return alert('Введите название сквада!');

    try {
      const res = await fetch('/api/squads/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + authToken
        },
        body: JSON.stringify({ name: n, passcode: p })
      });
      const data = await res.json();
      if (res.ok) {
        currentUser = data.user;
        squadModal.classList.add('hidden');
        updateAuthUI();
        socket.emit('auth_socket', { token: authToken });
      } else {
        alert(data.error || 'Ошибка вступления');
      }
    } catch (e) {
      alert('Ошибка сети');
    }
  });

  // Выход из сквада
  document.getElementById('btn-leave-squad')?.addEventListener('click', async () => {
    if (!confirm('Покинуть сквад? Вы потеряете доступ к общим гаражам отряда.')) return;
    try {
      const res = await fetch('/api/squads/leave', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + authToken
        }
      });
      const data = await res.json();
      if (res.ok) {
        currentUser = data.user;
        squadModal.classList.add('hidden');
        updateAuthUI();
        socket.emit('auth_socket', { token: authToken });
      }
    } catch (e) {
      alert('Ошибка сети');
    }
  });

  // Роспуск / удаление сквада командиром
  document.getElementById('btn-disband-squad')?.addEventListener('click', async () => {
    if (!confirm('ВНИМАНИЕ! Вы уверены, что хотите РАСПУСТИТЬ и ПОЛНОСТЬЮ УДАЛИТЬ этот сквад? Все участники вернутся в соло-режим.')) return;
    try {
      const res = await fetch('/api/squads/disband', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + authToken
        }
      });
      const data = await res.json();
      if (res.ok) {
        currentUser.squadId = null;
        currentSquadData = null;
        claimsData = currentUser.personalGarages || {};
        updateBuildingsVisuals();
        renderClaimsTable();
        squadModal.classList.add('hidden');
        updateAuthUI();
        socket.emit('auth_socket', { token: authToken });
      } else {
        alert(data.error || 'Ошибка при роспуске сквада');
      }
    } catch (e) {
      alert('Ошибка сети');
    }
  });

  // Смена пароля сквада командиром
  document.getElementById('btn-save-squad-passcode')?.addEventListener('click', async () => {
    const p = document.getElementById('squad-passcode-input').value.trim();
    try {
      const res = await fetch('/api/squads/passcode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + authToken
        },
        body: JSON.stringify({ newPasscode: p })
      });
      const data = await res.json();
      if (res.ok) {
        alert('Пароль сквада успешно обновлён!');
      } else {
        alert(data.error || 'Ошибка смены пароля');
      }
    } catch (e) {
      alert('Ошибка сети');
    }
  });

  // Запуск авторизации
  initAuth();

  // ======================================================================
  //  11. МОДАЛКА СПИСКА ГАРАЖЕЙ И МАССОВАЯ СМЕНА ПАРОЛЕЙ
  // ======================================================================
  const claimsModal = document.getElementById('claims-modal');
  document.getElementById('btn-claims-list').addEventListener('click', () => {
    renderClaimsTable();
    claimsModal.classList.remove('hidden');
  });
  document.getElementById('modal-claims-close').addEventListener('click', () => claimsModal.classList.add('hidden'));

  function normalizeDP(s) {
    if (!s) return '';
    return String(s).toLowerCase().replace(/дп/g, 'dp').replace(/[\s\-_]/g, '');
  }

  function ruToEn(str) {
    const map = {
      'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh',
      'з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o',
      'п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'ch','ц':'ts',
      'ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'
    };
    return str.toLowerCase().split('').map(ch => map[ch] !== undefined ? map[ch] : ch).join('');
  }

  function switchLayout(s) {
    const enToRu = {
      'q':'й','w':'ц','e':'у','r':'к','t':'е','y':'н','u':'г','i':'ш','o':'щ','p':'з','[':'х',']':'ъ',
      'a':'ф','s':'ы','d':'в','f':'а','g':'п','h':'р','j':'о','k':'л','l':'д',';':'ж','\'':'э',
      'z':'я','x':'ч','c':'с','v':'м','b':'и','n':'т','m':'ь',',':'б','.':'ю'
    };
    const ruToEn = {};
    for (const [k, v] of Object.entries(enToRu)) ruToEn[v] = k;
    return s.split('').map(ch => ruToEn[ch] || enToRu[ch] || ch).join('');
  }

  const ALTIS_NAMES_RU = {
    'kavala': 'кавала',
    'pyrgos': 'пиргос',
    'athira': 'атира афира',
    'sofia': 'софия',
    'zaros': 'зарос',
    'neochori': 'неохори',
    'panochori': 'панохори',
    'neri': 'нери',
    'aggelochori': 'аггелохори ангелохори',
    'paros': 'парос',
    'kalochori': 'калохори',
    'chalkeia': 'халкия халкея',
    'charkia': 'харкия чаркия',
    'agios dionysios': 'агиос дионисиос',
    'agios konstantinos': 'агиос константинос',
    'agios petros': 'агиос петрос',
    'agia triada': 'агиа триада айя триада',
    'abdera': 'абдера',
    'alikampos': 'аликампос',
    'anthrakia': 'антракия анфракия',
    'delfinaki': 'дельфинаки',
    'dorida': 'дорида',
    'ekali': 'экали екали',
    'feres': 'ферес',
    'frini': 'фрини',
    'galati': 'галати',
    'gravia': 'гравия',
    'ifestiona': 'ифестиона',
    'ioannina': 'иоаннина',
    'kalithea': 'калитея калифея',
    'katalaki': 'каталаки',
    'kore': 'коре',
    'koroni': 'корони',
    'lakka': 'лакка',
    'molos': 'молос',
    'negades': 'негадес',
    'nifi': 'нифи',
    'oreokastro': 'ореокастро',
    'orino': 'орино',
    'panagia': 'панагия',
    'poliakko': 'полиакко',
    'rodopoli': 'родополи',
    'selakano': 'селакано',
    'stavros': 'ставрос',
    'syrta': 'сирта',
    'telos': 'телос',
    'therisa': 'териса фериса',
    'topolia': 'тополия',
    'zeloran': 'зелоран',
    'drimea': 'дримея',
    'edessa': 'эдесса едесса',
    'vikos': 'викос',
    'trachia': 'трахия тракия',
    'mazi': 'мази',
    'livadi': 'ливади',
    'limni': 'лимни',
    'almyra': 'алмира алмыра',
    'iraklia': 'ираклия',
    'nidasos': 'нидасос',
    'gatolia': 'гатолия',
    'polemistia': 'полемистия',
    'limnichori': 'лимнихори',
    'sideras': 'сидерас',
    'bomos': 'бомос',
    'aristi': 'аристи',
    'fotia': 'фотия',
    'gori': 'гори',
    'krya nera': 'крия нера крыа нера',
    'amfissa': 'амфисса амфиса',
    'kastro': 'кастро',
    'faros': 'фарос'
  };

  function matchGarageSearch(c, lm, filter) {
    if (!filter) return true;
    const f = filter.toLowerCase().trim();
    const fSwitched = switchLayout(f).toLowerCase().trim();
    const fEn = ruToEn(f);

    // 1. Поиск по DP (дп 7, дп7, dp 7, dp7, dp-7...)
    const fNormDP = normalizeDP(f);
    const fSwitchedDP = normalizeDP(fSwitched);
    if (lm.dpName) {
      const dpNorm = normalizeDP(lm.dpName);
      if ((fNormDP.startsWith('dp') && dpNorm.includes(fNormDP)) ||
          (fSwitchedDP.startsWith('dp') && dpNorm.includes(fSwitchedDP))) {
        return true;
      }
      if ((dpNorm.includes(fNormDP) && fNormDP.length >= 2) ||
          (dpNorm.includes(fSwitchedDP) && fSwitchedDP.length >= 2)) {
        return true;
      }
    }

    // 2. Поиск по городу/локации (русский и английский: zeloran = зелоран, kavala = кавала...)
    if (lm.cityName) {
      const cn = lm.cityName.toLowerCase();
      const ruAliases = ALTIS_NAMES_RU[cn] || '';
      if (cn.includes(f) || cn.includes(fEn) || cn.includes(fSwitched)) return true;
      if (ruAliases.includes(f) || ruAliases.includes(fSwitched)) return true;
    }

    // 3. Стандартные поля гаража: владелец, ID, тип, пароль
    return (c.owner    && (c.owner.toLowerCase().includes(f) || c.owner.toLowerCase().includes(fSwitched))) ||
           (c.type     && (c.type.toLowerCase().includes(f) || c.type.toLowerCase().includes(fSwitched))) ||
           (c.password && (c.password.toLowerCase().includes(f))) ||
           (c.id       && (c.id.toLowerCase().includes(f) || c.id.toLowerCase().includes(fSwitched)));
  }

  function renderClaimsTable() {
    const tbody = document.getElementById('claims-table-body');
    const filter = (document.getElementById('search-claims-input')?.value || '').toLowerCase().trim();
    tbody.innerHTML = '';

    const list = Object.values(claimsData).filter(c => {
      const lm = getGarageLandmark(c.x, c.y);
      return matchGarageSearch(c, lm, filter);
    });

    if (!list.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center">Нет сохраненных гаражей</td></tr>';
      return;
    }

    // Сортировка: Сначала наши 🟢, потом друзья 🟣, склад 🟡, враги 🔴, свободные ⚪
    const statusPriority = { friendly: 1, ally: 2, loot: 3, hostile: 4, neutral: 5 };
    list.sort((a, b) => {
      const pA = statusPriority[a.status] || 1;
      const pB = statusPriority[b.status] || 1;
      if (pA !== pB) return pA - pB;
      const lmA = getGarageLandmark(a.x, a.y);
      const lmB = getGarageLandmark(b.x, b.y);
      return (lmA.cityName || '').localeCompare(lmB.cityName || '');
    });

    list.forEach(c => {
      const tr = document.createElement('tr');
      const icon = c.status === 'hostile' ? '🔴 Враг'
        : c.status === 'ally' ? '🟣 Друг'
        : c.status === 'loot' ? '🟡 Склад'
        : c.status === 'neutral' ? '⚪ Свободен'
        : '🟢 Наш';

      const lm = getGarageLandmark(c.x, c.y);

      tr.innerHTML = `
        <td>${icon}</td>
        <td><b>${(c.type || '').replace(/^Land_/, '')}</b><br><small style="color:#8b949e">${c.id}</small></td>
        <td style="font-size:12px; line-height:1.45;">
          ${lm.cityName ? `<div style="font-weight:600; color:#e6edf3;">🏙️ ${lm.cityName} <small style="color:#8b949e; font-weight:normal;">(${lm.cityFormattedDist})</small></div>` : ''}
          ${lm.dpName ? `<div style="color:#e3b341; font-weight:500;">📦 ${lm.dpName} <small style="color:#8b949e; font-weight:normal;">(${lm.dpFormattedDist})</small></div>` : ''}
          <div style="font-family:var(--font-mono); font-size:11px; color:#58a6ff; margin-top:2px;">X: ${Math.round(c.x)} | Y: ${Math.round(c.y)}</div>
        </td>
        <td style="color:#58a6ff">${c.owner || '—'}</td>
        <td><code>${c.password ? '••••••' : '—'}</code></td>
        <td><button class="btn btn-secondary" data-fly="${c.id}" data-x="${c.x}" data-y="${c.y}">НАЙТИ</button></td>`;
      tbody.appendChild(tr);
    });

    tbody.querySelectorAll('[data-fly]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.fly;
        const x = parseFloat(btn.dataset.x);
        const y = parseFloat(btn.dataset.y);
        claimsModal.classList.add('hidden');
        map.flyTo(gameToLatLng(x, y), 6, { duration: 1.2 });
        const p = buildingPolygons[id];
        if (p) setTimeout(() => p.fire('click'), 1300);
      });
    });
  }

  document.getElementById('search-claims-input')?.addEventListener('input', renderClaimsTable);

  async function performBulkPasswordChange(newPassword, msgElement) {
    if (!currentUser) {
      alert('Пожалуйста, сначала авторизуйтесь!');
      return;
    }
    const cleanPass = String(newPassword !== undefined ? newPassword : '').trim();
    if (!cleanPass) {
      if (!confirm('Вы оставили пароль пустым. Снять пароль со всех наших зеленых гаражей (Наш гараж / База)?')) {
        return;
      }
    } else {
      if (!confirm(`Установить новый пароль "${cleanPass}" на ВСЕ гаражи со статусом 🟢 «Наш гараж»?`)) {
        return;
      }
    }

    if (msgElement) {
      msgElement.style.display = 'block';
      msgElement.style.color = '#58a6ff';
      msgElement.textContent = 'Обновление паролей...';
    }

    try {
      const res = await fetch('/api/squads/bulk_password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ newPassword: cleanPass })
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        if (msgElement) {
          msgElement.style.color = '#f85149';
          msgElement.textContent = `Ошибка: ${data.error || 'Не удалось сменить пароли'}`;
        } else {
          alert(`Ошибка: ${data.error || 'Не удалось сменить пароли'}`);
        }
        return;
      }

      if (data.claims) {
        claimsData = data.claims;
        updateBuildingsVisuals();
        renderClaimsTable();
      }

      const countMsg = `Успешно! Обновлено гаражей: ${data.count || 0}. Пароль изменен на: ${cleanPass ? '••••••' : 'без пароля'}`;
      if (msgElement) {
        msgElement.style.color = '#3fb950';
        msgElement.textContent = countMsg;
        setTimeout(() => { msgElement.style.display = 'none'; }, 6000);
      } else {
        alert(countMsg);
      }
    } catch (e) {
      console.error(e);
      if (msgElement) {
        msgElement.style.color = '#f85149';
        msgElement.textContent = 'Ошибка сети при смене паролей';
      }
    }
  }

  document.getElementById('btn-bulk-change-password')?.addEventListener('click', () => {
    const val = document.getElementById('bulk-garage-password-input')?.value;
    const msg = document.getElementById('bulk-pass-status-msg');
    performBulkPasswordChange(val, msg);
  });

  document.getElementById('btn-bulk-change-password-quick')?.addEventListener('click', () => {
    const val = document.getElementById('bulk-garage-password-input-quick')?.value;
    const msg = document.getElementById('bulk-pass-quick-msg');
    performBulkPasswordChange(val, msg);
  });

  // ======================================================================
  //  12. ПАНЕЛЬ «НАСТРОЙКА КАРТЫ» (ФИЛЬТРАЦИЯ 11 КАТЕГОРИЙ И ПОИСК)
  // ======================================================================
  const settingsPanel = document.getElementById('map-settings-panel');
  const btnToggleSettings = document.getElementById('btn-toggle-settings-dialog');
  const btnSettingsClose  = document.getElementById('btn-settings-close');

  // Открытие/закрытие панели настроек
  btnToggleSettings?.addEventListener('click', () => {
    settingsPanel.classList.toggle('hidden');
    btnToggleSettings.classList.toggle('active', !settingsPanel.classList.contains('hidden'));
  });

  btnSettingsClose?.addEventListener('click', () => {
    settingsPanel.classList.add('hidden');
    btnToggleSettings?.classList.remove('active');
  });

  // Перемещение панели за заголовок (Draggable)
  const dragHandle = document.getElementById('settings-drag-handle');
  if (dragHandle && settingsPanel) {
    let isDragging = false;
    let dragStartX = 0, dragStartY = 0, panelStartX = 0, panelStartY = 0;

    dragHandle.addEventListener('mousedown', (e) => {
      if (e.target.closest('button')) return;
      isDragging = true;
      dragStartX = e.clientX;
      dragStartY = e.clientY;
      const rect = settingsPanel.getBoundingClientRect();
      panelStartX = rect.left;
      panelStartY = rect.top;
      document.addEventListener('mousemove', onDragMove);
      document.addEventListener('mouseup', onDragEnd);
    });

    function onDragMove(e) {
      if (!isDragging) return;
      const dx = e.clientX - dragStartX;
      const dy = e.clientY - dragStartY;
      const newX = Math.max(10, Math.min(window.innerWidth - 305, panelStartX + dx));
      const newY = Math.max(55, Math.min(window.innerHeight - 150, panelStartY + dy));
      settingsPanel.style.left = `${newX}px`;
      settingsPanel.style.top  = `${newY}px`;
    }

    function onDragEnd() {
      isDragging = false;
      document.removeEventListener('mousemove', onDragMove);
      document.removeEventListener('mouseup', onDragEnd);
    }
  }

  // 11 Чекбоксов категорий
  const catNames = [
    'names', 'resources', 'routes', 'shops', 'infra', 
    'realestate', 'dp', 'bases', 'illegal', 'other', 'territories'
  ];

  function isCategoryChecked(cat) {
    const chk = document.getElementById(`chk-cat-${cat}`);
    return chk ? chk.checked : true;
  }

  function saveCategoryFilters() {
    try {
      const state = {};
      catNames.forEach(cat => {
        const chk = document.getElementById(`chk-cat-${cat}`);
        if (chk) state[cat] = chk.checked;
      });
      localStorage.setItem('altis_category_filters', JSON.stringify(state));
    } catch (e) {}
  }

  function loadSavedCategoryFilters() {
    try {
      const raw = localStorage.getItem('altis_category_filters');
      if (!raw) return;
      const state = JSON.parse(raw);
      catNames.forEach(cat => {
        if (typeof state[cat] === 'boolean') {
          const chk = document.getElementById(`chk-cat-${cat}`);
          const lyr = categoryLayers[cat];
          if (chk) chk.checked = state[cat];
          if (lyr) {
            state[cat] ? map.addLayer(lyr) : map.removeLayer(lyr);
          }
        }
      });
    } catch (e) {}
  }

  catNames.forEach(cat => {
    const chk = document.getElementById(`chk-cat-${cat}`);
    if (!chk) return;
    chk.addEventListener('change', () => {
      const lyr = categoryLayers[cat];
      if (!lyr) return;
      if (chk.checked) {
        map.addLayer(lyr);
      } else {
        map.removeLayer(lyr);
      }
      saveCategoryFilters();
      // Перепроверяем фильтрацию при поиске
      const q = (document.getElementById('settings-search-input')?.value || '').trim().toLowerCase();
      if (q) filterMarkersByQuery(q);
    });
  });

  // Восстанавливаем сохраненные настройки фильтров маркеров из localStorage
  loadSavedCategoryFilters();

  // Клик по всей строке категории переключает чекбокс
  document.querySelectorAll('.settings-row').forEach(row => {
    row.addEventListener('click', (e) => {
      if (e.target.closest('input') || e.target.closest('button') || e.target.closest('.settings-row-actions')) return;
      const chk = row.querySelector('input[type="checkbox"]');
      if (chk) {
        chk.checked = !chk.checked;
        chk.dispatchEvent(new Event('change'));
      }
    });
  });

  // Быстрое включение/отключение всех категорий
  function setAllCategories(val) {
    catNames.forEach(cat => {
      const chk = document.getElementById(`chk-cat-${cat}`);
      if (chk) {
        chk.checked = val;
        const lyr = categoryLayers[cat];
        if (lyr) {
          val ? map.addLayer(lyr) : map.removeLayer(lyr);
        }
      }
    });
    saveCategoryFilters();
    const q = (document.getElementById('settings-search-input')?.value || '').trim().toLowerCase();
    if (q) filterMarkersByQuery(q);
  }

  // Поиск по карте в реальном времени
  const searchInput = document.getElementById('settings-search-input');
  const btnSearchPrev = document.getElementById('btn-search-prev');
  const btnSearchNext = document.getElementById('btn-search-next');
  let currentSearchResults = [];
  let currentSearchIdx = 0;

  function filterMarkersByQuery(query) {
    currentSearchResults = [];
    currentSearchIdx = 0;
    const q = (query || '').toLowerCase().trim();
    const hasQuery = q.length > 0;
    const qSwitched = switchLayout(q).toLowerCase().trim();
    const qEn = ruToEn(q);
    const qNormDP = normalizeDP(q);

    allMarkerEntries.forEach(entry => {
      const m = entry.data;
      let match = !hasQuery;
      if (hasQuery) {
        const text = (m.text || '').toLowerCase();
        const name = (m.name || '').toLowerCase();
        const type = (m.type || '').toLowerCase();
        const normDP = normalizeDP(text) || normalizeDP(name);

        match = text.includes(q) || text.includes(qSwitched) || text.includes(qEn) ||
                name.includes(q) || name.includes(qSwitched) || name.includes(qEn) ||
                type.includes(q) ||
                (qNormDP.startsWith('dp') && normDP.includes(qNormDP)) ||
                (normDP.includes(qNormDP) && qNormDP.length >= 2);
      }

      const catChecked = isCategoryChecked(entry.cat);
      const lyr = categoryLayers[entry.cat];

      if (match && catChecked) {
        if (!lyr.hasLayer(entry.marker)) lyr.addLayer(entry.marker);
        if (hasQuery) currentSearchResults.push(entry);
      } else {
        if (lyr.hasLayer(entry.marker)) lyr.removeLayer(entry.marker);
      }
    });
  }

  searchInput?.addEventListener('input', () => {
    const q = searchInput.value.trim().toLowerCase();
    filterMarkersByQuery(q);
  });

  function focusSearchResult(entry) {
    if (!entry) return;
    const m = entry.data;
    map.flyTo(gameToLatLng(m.x, m.y), 6, { duration: 0.8 });
    setTimeout(() => {
      entry.marker.openTooltip();
    }, 850);
  }

  // Кнопка <: Предыдущий результат или "Снять все" если поиск пуст
  btnSearchPrev?.addEventListener('click', () => {
    const q = (searchInput?.value || '').trim().toLowerCase();
    if (q.length > 0 && currentSearchResults.length > 0) {
      currentSearchIdx = (currentSearchIdx - 1 + currentSearchResults.length) % currentSearchResults.length;
      focusSearchResult(currentSearchResults[currentSearchIdx]);
    } else {
      setAllCategories(false);
    }
  });

  // Кнопка >: Следующий результат или "Выбрать все" если поиск пуст
  btnSearchNext?.addEventListener('click', () => {
    const q = (searchInput?.value || '').trim().toLowerCase();
    if (q.length > 0 && currentSearchResults.length > 0) {
      currentSearchIdx = (currentSearchIdx + 1) % currentSearchResults.length;
      focusSearchResult(currentSearchResults[currentSearchIdx]);
    } else {
      setAllCategories(true);
    }
  });

  // Действия для 11-й строки (Территории):
  // 1. Показать все зоны (Zoom to fit)
  document.getElementById('btn-territory-fit')?.addEventListener('click', (e) => {
    e.stopPropagation();
    if (territoryBounds.isValid()) {
      map.fitBounds(territoryBounds.pad(0.08), { duration: 1.0 });
    }
  });

  // 2. Список территорий (Модалка)
  const territoriesModal = document.getElementById('territories-modal');
  document.getElementById('btn-territory-list')?.addEventListener('click', (e) => {
    e.stopPropagation();
    renderTerritoriesModal();
    territoriesModal?.classList.remove('hidden');
  });

  document.getElementById('modal-territories-close')?.addEventListener('click', () => {
    territoriesModal?.classList.add('hidden');
  });

  function renderTerritoriesModal() {
    const ul = document.getElementById('territories-list-items');
    if (!ul) return;
    ul.innerHTML = '';

    if (!territoriesList.length) {
      ul.innerHTML = '<li class="empty-list">Нет доступных территорий</li>';
      return;
    }

    territoriesList.forEach(z => {
      const li = document.createElement('li');
      li.innerHTML = `
        <div style="display:flex; align-items:center;">
          <span class="zone-color-indicator" style="background:${z.color}"></span>
          <b>${z.label}</b>
        </div>
        <span style="font-family:var(--font-mono); font-size:12px; color:var(--text-muted);">
          R: ${z.radius_x}м • [${z.x}, ${z.y}]
        </span>
      `;
      li.addEventListener('click', () => {
        territoriesModal.classList.add('hidden');
        map.flyTo(gameToLatLng(z.x, z.y), 6, { duration: 1.0 });
      });
      ul.appendChild(li);
    });
  }

  // 3. Редактор зон
  document.getElementById('btn-territory-edit')?.addEventListener('click', (e) => {
    e.stopPropagation();
    alert('Режим разметки зон: для добавления новой зоны в uploaded_mission.cpp укажите координаты и радиус.');
  });

  // 4. Опции прозрачности зон
  let zoneOpacity = 0.22;
  document.getElementById('btn-territory-menu')?.addEventListener('click', (e) => {
    e.stopPropagation();
    zoneOpacity = zoneOpacity === 0.22 ? 0.5 : (zoneOpacity === 0.5 ? 0.1 : 0.22);
    categoryLayers.territories.eachLayer(l => {
      if (l.setStyle) l.setStyle({ fillOpacity: zoneOpacity });
    });
  });

  // ======================================================================
  //  13. ДОПОЛНИТЕЛЬНЫЕ КНОПКИ ВЕРХНЕЙ ПАНЕЛИ HUD
  // ======================================================================
  // Переключатель кастомных дорог выключен вместе с самим слоем; см. блок выше.

  let gridOn = false;
  document.getElementById('btn-toggle-grid')?.addEventListener('click', function() {
    gridOn = !gridOn;
    this.classList.toggle('active', gridOn);
    gridOn ? map.addLayer(gridLayer) : map.removeLayer(gridLayer);
  });
});
