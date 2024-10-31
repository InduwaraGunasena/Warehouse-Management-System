import React, { useState, useEffect } from "react";
import Card from "../../components/card/Card";
import Loader from "../../components/loader/Loader";
import "./Warehouse.scss";
import { toast } from "react-toastify";
import axios from "axios"; // Import axios for making requests


const Warehouse = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [unit, setUnit] = useState(0); // State for rack units
  const maxUnits = parseInt(5, 10); // Get max units from .env
  const [isConfirmed, setIsConfirmed] = useState(false); // Track if confirmed

  // Fetch saved units on page load
  useEffect(() => {
    const fetchRackUnits = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/api/warehouse`
        );
        setUnit(response.data.unit);
      } catch (error) {
        console.error("Error fetching rack units:", error);
        toast.error("Failed to load rack units");
      } finally{
        setIsLoading(false); 
      }
    };
    fetchRackUnits();
  }, []);

   if (isLoading) {
     return <Loader />; // Show loader while loading
   }
   
  // Function to reset the units to zero
  const resetRackUnits = () => {
    setUnit(0);
    setIsConfirmed(false); // Add a call to your backend API to reset the units in the DB as well
  };

  // Function to save the updated rack units to the backend
  const saveRackUnits = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      // Here you can call the API to save the updated number of units to your DB
      await axios.patch(
        `${process.env.REACT_APP_BACKEND_URL}/api/warehouse/update`,
        { unit }
      );
      setIsLoading(false);
      setIsConfirmed(true);
      toast.success("Rack units updated successfully");
    } catch (error) {
      console.log(error);
      setIsLoading(false);
      toast.error(error.message);
    }
  };

  return (
    <div className="warehouse">
      {isLoading && <Loader />}
      <Card cardClass={"card"}>
        <h3>Rack Units Manager</h3>
        <p>
          Note: Users can only configure a single-row rack with one shelf. This
          single rack must contain up to 5 boxes.
        </p>

        <span>
          <div className="unit-buttons">
            <button
              onClick={() => setUnit((prev) => Math.min(maxUnits, prev + 1))}
            >
              {" "}
              +{" "}
            </button>

            <dev className="unit-box">
              <input
                type="number"
                value={unit}
                onChange={(e) =>
                  setUnit(Math.max(0, Math.min(maxUnits, e.target.value)))
                }
                min={0}
                max={maxUnits} // Constrain the value between 0 and maxUnits
              />
            </dev>

            <button onClick={() => setUnit((prev) => Math.max(0, prev - 1))}>
              {" "}
              -{" "}
            </button>
          </div>
        </span>

        <button className="btn" onClick={resetRackUnits}>
          {" "}
          Reset{" "}
        </button>
        <button
          className="btn confirm-btn"
          onClick={saveRackUnits}
          style={{ marginLeft: "10px" }}
        >
          Confirm
        </button>
      </Card>

      <div className="rack-visualization">
        {[...Array(unit)].map((_, index) => (
          <div
            key={index}
            className="box"
            style={{ backgroundColor: isConfirmed ? "#007bff" : "grey" }}
          ></div>
        ))}
        {unit === 0 && <p>Empty Rack</p>}
      </div>
    </div>
  );
};

export default Warehouse;
