const mongoose = require("mongoose");

const productSchema = mongoose.Schema(
  {
    position: {
      type: Number,
      default: 0,
    },
    marker_ID: {
      type: String,
      default: "0",
    },
    image: {
      type: Object,
      default: {},
    },
    // Optional: status field
    status: {
      type: String,
      enum: ["not_scanned", "scanned"],
      default: "not_scanned",
    },
  },
  {
    timestamps: true,
  }
);

const Product = mongoose.model("Product", productSchema);
module.exports = Product;
