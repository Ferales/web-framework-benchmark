const express = require("express");
const bodyParser = require("body-parser");
const authRoutes = require("./routes/auth");
const protectedRoutes = require("./routes/protected");
const filesRoutes = require("./routes/files");
const { Sequelize } = require("sequelize");
const { User, Product, Order, OrderProduct } = require("./models");
const db = require("./models");
const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use("/api/auth", authRoutes);
app.use("/api", protectedRoutes);
app.use("/api", filesRoutes);

app.get("/api/users", async (req, res) => {
  const users = await User.findAll();
  res.json(users);
});

app.get("/api/users/:id", async (req, res) => {
  const { id } = req.params;
  const user = await User.findByPk(id);
  res.json(user);
});

app.post("/api/users", async (req, res) => {
  const { name, email, password, age } = req.body;
  const user = await User.create({ name, email, password, age });
  res.status(201).json(user);
});

app.put("/api/users/:id", async (req, res) => {
  const { id } = req.params;
  const { name, email } = req.body;
  const user = await User.findByPk(id);

  if (user) {
    user.name = name;
    user.email = email;
    await user.save();
    res.json(user);
  } else {
    res.status(404).send("Użytkownik nie znaleziony");
  }
});

app.delete("/api/users/:id", async (req, res) => {
  const { id } = req.params;
  const user = await User.findByPk(id);

  if (user) {
    await user.destroy();
    res.status(204).send();
  } else {
    res.status(404).send("Użytkownik nie znaleziony");
  }
});

// 1. Pobranie n najtańszych/najdroższych produktów z paginacją
app.get("/api/products", async (req, res) => {
  const { limit = 10, offset = 0, direction = "ASC" } = req.query;

  try {
    const products = await OrderProduct.findAll({
      order: [["price", direction.toUpperCase() === "DESC" ? "DESC" : "ASC"]],
      limit: parseInt(limit),
      offset: parseInt(offset),
    });

    res.json(products);
  } catch (error) {
    res.status(500).json({ error: "Błąd podczas pobierania produktów" });
  }
});

// 2. Pobranie 10 najpopularniejszych produktów (na podstawie ilości zamówień)
app.get("/api/products/popular", async (req, res) => {
  try {
    const popularProducts = await db.sequelize.query(
      `SELECT 
        p.id, 
        p.name, 
        p.price, 
        COALESCE(SUM(op.quantity), 0) as total_quantity
       FROM 
        products p
       LEFT JOIN 
        order_products op ON p.id = op.product_id
       GROUP BY 
        p.id, p.name, p.price
       ORDER BY 
        total_quantity DESC
       LIMIT 10`,
      {
        type: db.sequelize.QueryTypes.SELECT,
        model: db.Product,
        mapToModel: true,
      }
    );

    res.json(popularProducts);
  } catch (error) {
    console.error("Error fetching popular products:", error);
    res.status(500).json({
      error: "Error fetching popular products",
      details: error.message,
    });
  }
});

// 3. Pobranie zamówień użytkownika w podanym przedziale czasowym z filtrem statusu
app.get("/api/orders", async (req, res) => {
  const { userId, startDate, endDate, status = "Pending" } = req.query;

  const validStatuses = ["Pending", "Completed", "Cancelled"];
  if (!validStatuses.includes(status)) {
    return res.status(400).json({ error: "Nieprawidłowy status zamówienia" });
  }

  if (!userId || !startDate || !endDate) {
    return res
      .status(400)
      .json({ error: "Wymagane parametry: userId, startDate, endDate" });
  }

  try {
    const orders = await Order.findAll({
      where: {
        user_id: userId,
        order_date: {
          [db.Sequelize.Op.between]: [new Date(startDate), new Date(endDate)],
        },
        status,
      },
      include: [
        {
          model: Product,
          through: { attributes: ["quantity"] },
          as: "orders",
        },
      ],
    });

    res.json(orders);
  } catch (error) {
    console.error("Error fetching user orders:", error);
    res.status(500).json({
      error: "Błąd podczas pobierania zamówień użytkownika",
      details: error.message,
    });
  }
});

app.listen(port, () => {
  console.log(`Serwer działa na http://localhost:${port}`);
});
