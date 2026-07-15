const express = require("express");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
const User = require("../models/user");
const router = express.Router();

router.post("/register", async (req, res) => {
  try {
    const { name, password, email } = req.body;

    if (!name || !password || !email) {
      return res.status(400).json({ error: "Brak danych rejestracyjnych" });
    }

    const existingUser = await User.findOne({ where: { email } });

    if (existingUser) {
      return res.status(400).json({ error: "Użytkownik już istnieje" });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const user = await User.create({ name, password: hashedPassword, email });

    res.status(201).json({ msg: "Użytkownik zarejestrowany", user });
  } catch (err) {
    console.error("Błąd serwera:", err);
    res.status(500).json({ msg: "Błąd serwera", err: err.message });
  }
});

router.post("/login", async (req, res) => {
  try {
    console.log("🔹 Otrzymano dane logowania:", req.body);

    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: "Brak danych logowania" });
    }

    const user = await User.findOne({ where: { email } });

    if (!user) {
      return res.status(401).json({ error: "Nieprawidłowy email lub hasło" });
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);

    if (!isPasswordValid) {
      return res.status(401).json({ error: "Nieprawidłowy email lub hasło" });
    }

    const token = jwt.sign({ email: user.email }, "SECRET_KEY", {
      expiresIn: "1h",
    });

    res.json({ token });
  } catch (err) {
    console.error("Błąd serwera:", err);
    res.status(500).json({ msg: "Błąd serwera", err: err.message });
  }
});

module.exports = router;
