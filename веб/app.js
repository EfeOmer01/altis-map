/* === ТАКТИЧЕСКАЯ КАРТА ARMA 3 ALTIS — v4 ПОЛНОЕ СООТВЕТСТВИЕ ИГРЕ === */

document.addEventListener('DOMContentLoaded', () => {

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
    minZoom: 2,
    maxZoom: 8,
    zoomSnap: 1,
    zoomDelta: 1,
    attributionControl: false,
    maxBounds: mapBounds.pad(0.15),
    maxBoundsViscosity: 0.8
  });

  map.fitBounds(mapBounds);

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
  topoLayer.addTo(map);

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
  riverOverlay.addTo(map);

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

  let satelliteMode = false;
  const basemapButton = document.getElementById('btn-toggle-basemap');
  basemapButton?.addEventListener('click', () => {
    satelliteMode = !satelliteMode;
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

          if (c && c.owner) {
            return `<b>${g.name || 'Гараж'}</b><br>${typeBadge}<br>Владелец: <span style="color:#58a6ff">${c.owner}</span><br>Пароль: <code>${c.password ? '••••••' : 'Нет'}</code>`;
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
    const isMission = (g && g.source === 'mission');
    const defaultCol = isMission ? '#fbbf24' : '#00f0ff';

    if (!c || !c.owner) {
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
      hostile: '#f85149',
      loot: '#d29922',
      neutral: '#8b949e'
    };
    const col = palette[c.status] || palette.friendly;
    poly.setStyle({
      color: col,
      fillColor: col,
      fillOpacity: 0.85,
      weight: 3
    });
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
  const citiesLayer = categoryLayers.names;

  fetch('/api/cities')
    .then(r => r.json())
    .then(cities => {
      cities.forEach(c => {
        let cls = 'arma-city-village';
        let labelText = c.name;

        if (c.type === 'NameCityCapital') {
          cls = 'arma-city-capital';
          labelText = c.name.toUpperCase();
        } else if (c.type === 'NameCity') {
          cls = 'arma-city-normal';
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

  function cleanMarkerLabel(value) {
    return String(value || '')
      .replace(/^\s*amazingrp(?:g)?\.ru\s*\|\s*/i, '')
      .trim();
  }

  fetch('/api/markers')
    .then(r => r.json())
    .then(markers => {
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

  function renderSquadMembers(members) {
    const ul = document.getElementById('squad-members-list');
    if (!ul) return;
    ul.innerHTML = '';
    if (!members || members.length === 0) {
      ul.innerHTML = '<li class="empty-list">Нет участников</li>';
      return;
    }

    const isLeader = currentUser && currentSquadData && currentSquadData.leaderId === currentUser.id;
    const roleBadge = document.getElementById('active-user-role');
    if (roleBadge) {
      roleBadge.textContent = isLeader ? 'Командир' : 'Боец';
      roleBadge.style.borderColor = isLeader ? '#eab308' : '#3b82f6';
      roleBadge.style.color = isLeader ? '#fde047' : '#93c5fd';
    }

    const leaderPanel = document.getElementById('leader-control-panel');
    const disbandBtn = document.getElementById('btn-disband-squad');
    if (disbandBtn) {
      if (isLeader) disbandBtn.classList.remove('hidden');
      else disbandBtn.classList.add('hidden');
    }
    if (leaderPanel) {
      if (isLeader) {
        leaderPanel.classList.remove('hidden');
        const passIn = document.getElementById('squad-passcode-input');
        if (passIn && currentSquadData.passcode) passIn.value = currentSquadData.passcode;
      } else {
        leaderPanel.classList.add('hidden');
      }
    }

    members.forEach(m => {
      const li = document.createElement('li');
      li.className = 'member-item';

      const isOnline = currentOnlineIds.has(m.userId);
      const isMemberLeader = currentSquadData && currentSquadData.leaderId === m.userId;

      li.innerHTML = `
        <div class="member-info-col">
          <span class="member-status-dot ${isOnline ? 'online' : ''}" title="${isOnline ? 'В сети' : 'Не в сети'}"></span>
          <img src="${m.avatar || ('https://api.dicebear.com/7.x/bottts/svg?seed=' + m.userId)}" class="member-avatar" alt="">
          <span class="member-name">${m.name || 'Боец'} ${isMemberLeader ? '👑' : ''}</span>
        </div>
      `;

      if (isLeader && m.userId !== currentUser.id) {
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
        li.appendChild(kickBtn);
      }

      ul.appendChild(li);
    });
  }

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
    panelCoords.textContent = `X: ${b.x}, Y: ${b.y}`;

    const c = claimsData[b.id] || {};
    ownerIn.value  = c.owner    || (currentUser ? currentUser.name : '');
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
  //  10. МОДАЛКИ: АВТОРИЗАЦИЯ И СКВАДЫ
  // ======================================================================
  const authModal  = document.getElementById('auth-modal');
  const squadModal = document.getElementById('squad-modal');

  document.getElementById('btn-open-auth-modal')?.addEventListener('click', () => authModal.classList.remove('hidden'));
  document.getElementById('modal-auth-close')?.addEventListener('click', () => authModal.classList.add('hidden'));

  document.getElementById('btn-open-squad-modal')?.addEventListener('click', () => {
    if (!currentUser) {
      alert('Сначала войдите в аккаунт, чтобы создать сквад или управлять отрядом!');
      authModal.classList.remove('hidden');
      return;
    }
    squadModal.classList.remove('hidden');
  });
  document.getElementById('modal-squad-close')?.addEventListener('click', () => squadModal.classList.add('hidden'));

  // Логин по паролю
  document.getElementById('btn-auth-login')?.addEventListener('click', async () => {
    const u = document.getElementById('auth-username').value.trim();
    const p = document.getElementById('auth-password').value.trim();
    if (!u || !p) return showAuthMsg('Заполните логин и пароль', 'error');

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
        socket.emit('auth_socket', { token: authToken });
      } else {
        showAuthMsg(data.error || 'Ошибка входа', 'error');
      }
    } catch (e) {
      showAuthMsg('Ошибка сети', 'error');
    }
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
  //  11. МОДАЛКА СПИСКА БАЗ
  // ======================================================================
  const claimsModal = document.getElementById('claims-modal');
  document.getElementById('btn-claims-list').addEventListener('click', () => {
    renderClaimsTable();
    claimsModal.classList.remove('hidden');
  });
  document.getElementById('modal-claims-close').addEventListener('click', () => claimsModal.classList.add('hidden'));

  function renderClaimsTable() {
    const tbody = document.getElementById('claims-table-body');
    const filter = (document.getElementById('search-claims-input')?.value || '').toLowerCase();
    tbody.innerHTML = '';

    const list = Object.values(claimsData).filter(c =>
      (c.owner    && c.owner.toLowerCase().includes(filter)) ||
      (c.type     && c.type.toLowerCase().includes(filter)) ||
      (c.password && c.password.toLowerCase().includes(filter)) ||
      (c.id       && c.id.toLowerCase().includes(filter))
    );

    if (!list.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center">Нет сохраненных баз/гаражей</td></tr>';
      return;
    }

    list.forEach(c => {
      const tr = document.createElement('tr');
      const icon = c.status === 'hostile' ? '🔴 Враг' : c.status === 'loot' ? '🟡 Склад' : c.status === 'neutral' ? '⚪ Свободен' : '🟢 Наш';
      tr.innerHTML = `
        <td>${icon}</td>
        <td><b>${(c.type || '').replace(/^Land_/, '')}</b><br><small style="color:#8b949e">${c.id}</small></td>
        <td style="font-family:var(--font-mono);font-size:12px">X: ${c.x} | Y: ${c.y}</td>
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
      // Перепроверяем фильтрацию при поиске
      const q = (document.getElementById('settings-search-input')?.value || '').trim().toLowerCase();
      if (q) filterMarkersByQuery(q);
    });
  });

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
    const hasQuery = query.length > 0;

    allMarkerEntries.forEach(entry => {
      const m = entry.data;
      const match = !hasQuery ||
        (m.text && m.text.toLowerCase().includes(query)) ||
        (m.name && m.name.toLowerCase().includes(query)) ||
        (m.type && m.type.toLowerCase().includes(query));

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
