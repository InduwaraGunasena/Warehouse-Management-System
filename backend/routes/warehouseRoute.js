const express = require("express");
const router = express.Router();
const {
    getRack,
    resetRack,
    updateRack,
} = require("../controllers/warehouseController");

// Route to get the number of units in the rack
router.get("/", getRack);

// Route to reset the rack's units to 0
router.patch("/reset", resetRack);

// Route to update the units in the rack (increase/decrease units)
router.patch("/update", updateRack);

module.exports = router;
