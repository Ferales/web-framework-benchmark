const jwt = require("jsonwebtoken");
const SECRET_KEY = "super_secret_key";

module.exports = function (req, res, next) {
  const token = req.header("Authorization");
  if (!token)
    return res.status(401).json({ msg: "Brak tokena, autoryzacja odmówiona" });

  try {
    const decoded = jwt.verify(token.replace("Bearer ", ""), SECRET_KEY);
    req.user = decoded;
    next();
  } catch (err) {
    res.status(401).json({ msg: "Nieprawidłowy token" });
  }
};
