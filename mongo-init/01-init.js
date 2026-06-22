const dbName = process.env.MONGO_INITDB_DATABASE || "habits_db";
const appUser = process.env.MONGO_APP_USER || "habits_app";
const appPass = process.env.MONGO_APP_PASS || "habits_app";

const appDb = db.getSiblingDB(dbName);

appDb.createUser({
  user: appUser,
  pwd: appPass,
  roles: [{ role: "readWrite", db: dbName }],
});

appDb.createCollection("habits");
appDb.createCollection("users");
appDb.createCollection("ephemeral_events");

appDb.habits.createIndex({ user_id: 1, date: -1 });
appDb.habits.createIndex(
  { name: 1 },
  { partialFilterExpression: { status: "active" } }
);
appDb.ephemeral_events.createIndex({ created_at: 1 }, { expireAfterSeconds: 86400 });

const now = new Date();
appDb.users.insertMany([
  { username: "demo_user" },
  { username: "starter_user" },
]);

appDb.habits.insertMany([
  {
    name: "Leer 10 páginas",
    frequency: "daily",
    status: "active",
    user_id: "demo_user",
    date: now,
  },
  {
    name: "Entrenar 30 minutos",
    frequency: "3x/week",
    status: "active",
    user_id: "demo_user",
    date: now,
  },
  {
    name: "Planificar semana",
    frequency: "weekly",
    status: "archived",
    user_id: "starter_user",
    date: now,
  },
]);

appDb.ephemeral_events.insertMany([
  { type: "seed", created_at: now, details: "Inicializacion del entorno" },
]);
