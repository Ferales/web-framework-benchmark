const express = require("express");
const multer = require("multer");
const path = require("path");
const File = require("../models/file");
const router = express.Router();
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

router.post("/upload_file", upload.single("file_data"), async (req, res) => {
  try {
    const { name } = req.body;
    const fileData = req.file;

    if (!fileData) {
      return res.status(400).json({ error: "Brak pliku w żądaniu." });
    }

    const file = await File.create({
      name: name,
      file_data: fileData.buffer,
    });

    res.status(201).json({
      msg: "Plik zapisany pomyślnie",
      fileId: file.id,
    });
  } catch (error) {
    console.error("Błąd przy zapisie pliku:", error);
    res.status(500).json({ error: "Błąd serwera" });
  }
});

router.get("/download_file/:id", async (req, res) => {
  const fileId = req.params.id;

  try {
    const file = await File.findByPk(fileId);

    if (!file) {
      return res.status(404).json({ error: "Plik nie znaleziony" });
    }

    const fileBase64 = file.file_data.toString("base64");

    res.json({
      fileId: file.id,
      fileName: file.name,
      fileData: fileBase64,
    });
  } catch (error) {
    console.error("Błąd przy pobieraniu pliku:", error);
    res.status(500).json({ error: "Błąd serwera" });
  }
});

module.exports = router;
