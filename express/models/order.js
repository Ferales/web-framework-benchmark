const { Model, DataTypes } = require("sequelize");
const sequelize = require("../config/database");

class Order extends Model {
  static associate(models) {
    Order.belongsTo(models.User, {
      foreignKey: "user_id",
    });

    Order.belongsToMany(models.Product, {
      through: models.OrderProduct,
      as: "orders",
      foreignKey: "order_id",
      otherKey: "product_id",
    });
  }
}

Order.init(
  {
    user_id: {
      type: DataTypes.BIGINT,
      allowNull: false,
    },
    order_date: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
    },
    status: {
      type: DataTypes.STRING,
      defaultValue: "Pending",
      allowNull: false,
    },
  },
  {
    sequelize,
    modelName: "Order",
    tableName: "orders",
    timestamps: false,
  }
);

module.exports = Order;
