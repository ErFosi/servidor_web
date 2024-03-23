CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(255) NOT NULL,
    contraseña VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS actividades (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    tiempo INT NOT NULL DEFAULT 0,
    categoria VARCHAR(255) NOT NULL DEFAULT 'Otros',
    start_time_millis BIGINT NOT NULL DEFAULT 0,
    is_playing BOOLEAN NOT NULL DEFAULT false,
    id_usuario INT NOT NULL,
    fecha DATE NOT NULL,
    FOREIGN KEY (id_Usuario) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS ubicaciones (
    id SERIAL PRIMARY KEY,
    latitud DOUBLE PRECISION NOT NULL,
    longitud DOUBLE PRECISION NOT NULL,
    id_actividad INT NOT NULL,
    FOREIGN KEY (id_actividad) REFERENCES actividades(id)
);