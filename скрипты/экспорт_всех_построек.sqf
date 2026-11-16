/*
    Автор: Antigravity
    Назначение: Выгрузка всех построек карты (включая оригинальные объекты ландшафта и кастомные)
    Формат: Экспорт в буфер обмена и RPT лог
    Использование: Выполнить в консоли отладки (Debug Console) в редакторе Eden на нужной карте
*/

[] spawn {
    params [
        ["_center", [15360, 15360, 0], [[]]],
        ["_radius", 30000, [0]]
    ];

    systemChat "Начат экспорт построек карты...";
    private _types = [
        "BUILDING", "HOUSE", "CHURCH", "CHAPEL", "BUNKER", 
        "FORTRESS", "HOSPITAL", "RUIN", "TOURISM", "WATERTOWER"
    ];

    private _terrainObjs = nearestTerrainObjects [_center, _types, _radius, false, true];
    private _missionObjs = allMissionObjects "House" + allMissionObjects "Building";
    private _allObjs = (_terrainObjs + _missionObjs);

    // Удаляем дубликаты
    private _seenIds = createHashMap;
    private _exportList = [];

    {
        private _id = _x call BIS_fnc_netId;
        if (_id isEqualTo "") then {
            _id = format ["obj_%1", getPosWorld _x apply {round _x}];
        };

        if !(_id in _seenIds) then {
            _seenIds set [_id, true];

            private _pos = getPosWorld _x;
            private _dir = getDir _x;
            private _type = typeOf _x;
            private _box = boundingBoxReal _x;

            // _box: [[minX, minY, minZ], [maxX, maxY, maxZ]]
            private _min = _box select 0;
            private _max = _box select 1;
            private _width = abs ((_max select 0) - (_min select 0));
            private _length = abs ((_max select 1) - (_min select 1));
            private _height = abs ((_max select 2) - (_min select 2));

            // Сохраняем компактный массив: [ID, Класс, X, Y, Направление, Ширина, Длина, Высота]
            _exportList pushBack [
                _id,
                _type,
                round ((_pos select 0) * 10) / 10,
                round ((_pos select 1) * 10) / 10,
                round _dir,
                round (_width * 10) / 10,
                round (_length * 10) / 10,
                round (_height * 10) / 10
            ];
        };
    } forEach _allObjs;

    private _json = toJSON _exportList;
    copyToClipboard _json;
    diag_log text format ["[ЭКСПОРТ_ПОСТРОЕК] Успешно экспортировано %1 объектов. JSON скопирован в буфер обмена.", count _exportList];
    systemChat format ["Экспорт завершен! Выгружено %1 построек. Данные в буфере обмена (Ctrl+V).", count _exportList];
};
