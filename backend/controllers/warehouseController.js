const asyncHandler = require("express-async-handler");
const Warehouse = require("../models/warehouseModel");


// Get the number of units in the rack
const getRack = asyncHandler(async (req, res) => {
  const rack = await Warehouse.findOne();
  
  if (!rack) {
    return res.status(404).json({ message: "Rack not found" });
  }
  res.status(200).json(rack);
});


// Reset the no. of units in the rack
const resetRack = asyncHandler(async (req, res) => {
  const rack = await Warehouse.findOne();
  // if product doesnt exist
  if (!rack) {
    return res.status(404).json({ message: "Rack not found" });
  }
  
  rack.unit = 0;
  await rack.save();
  res.status(200).json({ message: "Rack is reset to 0 units", rack });
});

// Update the units in the rack
const updateRack = asyncHandler(async (req, res) => {
  const { unit } = req.body;
  const maxUnits = parseInt(process.env.RACK_MAX_UNITS, 10);
  
  // Validate the unit is between 0 and maxUnits
  if (unit < 0 || unit > maxUnits) {
    return res.status(400).json({ message: `Units must be between 0 and ${maxUnits}` });
  }

  // Update rack
  const rack = await Warehouse.findOne();
  if (!rack) {
    return res.status(404).json({ message: "Rack not found" });
  }

  rack.unit = unit;
  await rack.save();
  res.status(200).json({ message: "Rack updated", rack });
});

module.exports = {
  getRack,
  resetRack,
  updateRack,
};
