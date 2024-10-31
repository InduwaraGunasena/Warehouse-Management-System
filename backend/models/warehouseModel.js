const mongoose = require("mongoose");

const warehouseSchema = mongoose.Schema(
  {
    unit: {
      type: Number,
      required: [true, "Please add the number of units in the rack"],
      default: 0,
    },
    
  },
  {
    timestamps: true,
  }
);

const Warehouse = mongoose.model("Warehouse", warehouseSchema);
module.exports = Warehouse;
