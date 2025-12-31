const express = require("express");
const fs = require("fs-extra");
const path = require("path");

const app = express();
const PORT = 3000;

app.use(express.json());
app.use(express.static("public"));

const DB_DIR = "./databases";
const INDEX_FILE = "./db_index.json";

fs.ensureDirSync(DB_DIR);
fs.ensureFileSync(INDEX_FILE);

// CREATE DATABASE
app.post("/create", async (req, res) => {
  const { name, auth } = req.body;
  if (!name || !auth) return res.status(400).json({ error: "Missing fields" });

  const index = await fs.readJson(INDEX_FILE);

  if (index[name]) {
    return res.status(400).json({ error: "Database already exists" });
  }

  index[name] = { auth };
  await fs.writeJson(INDEX_FILE, index, { spaces: 2 });
  await fs.writeJson(`${DB_DIR}/${name}.json`, {}, { spaces: 2 });

  res.json({
    success: true,
    url: `/database/${name}?auth=${auth}`
  });
});

// ACCESS DATABASE
app.get("/database/:name", async (req, res) => {
  const { name } = req.params;
  const { auth } = req.query;

  const index = await fs.readJson(INDEX_FILE);

  if (!index[name] || index[name].auth !== auth) {
    return res.status(403).json({ error: "Invalid auth" });
  }

  const data = await fs.readJson(`${DB_DIR}/${name}.json`);
  res.json(data);
});

// WRITE DATA
app.post("/database/:name", async (req, res) => {
  const { name } = req.params;
  const { auth } = req.query;

  const index = await fs.readJson(INDEX_FILE);

  if (!index[name] || index[name].auth !== auth) {
    return res.status(403).json({ error: "Invalid auth" });
  }

  await fs.writeJson(`${DB_DIR}/${name}.json`, req.body, { spaces: 2 });
  res.json({ success: true });
});

app.listen(PORT, () => {
  console.log("JSON DB Maker running on port", PORT);
});
