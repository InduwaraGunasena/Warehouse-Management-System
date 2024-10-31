import React, { useState, useEffect } from "react";
import axios from "axios";
import "./WarehouseMap.scss";
import { FaSearchPlus } from "react-icons/fa"; // Import zoom icon


const WarehouseMap = () => {
  const [units, setUnits] = useState(0);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [zoomedImage, setZoomedImage] = useState(null); // Track zoomed image state

  useEffect(() => {
    const fetchWarehouseData = async () => {
      try {
        setLoading(true);

        // Fetch the unit count from warehouse schema
        const warehouseResponse = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/api/warehouse`
        );
        setUnits(warehouseResponse.data.unit);

        // Fetch product details for each unit
        const productResponse = await axios.get(
          `${process.env.REACT_APP_BACKEND_URL}/api/products`
        );
        setProducts(productResponse.data);

        setLoading(false);
      } catch (error) {
        console.error("Error fetching warehouse or product data:", error);
        setLoading(false);
      }
    };

    fetchWarehouseData();
  }, []);

  const handleBoxClick = (product) => {
    setSelectedProduct(product);
  };

  const handleZoomClick = (image) => {
    setZoomedImage(image); // Set the image for the zoom modal
  };

  return (
    <div className="warehouse-map">
      <hr />
      <div className="header">
        <h3>Warehouse Map</h3>
      </div>

      {loading ? (
        <div className="loader">Loading...</div>
      ) : units === 0 ? (
        <div className="msg">
          <p>
            There is no inventory in the rack. Please set the units in Warehouse
            section.
          </p>
        </div>
      ) : (
        <div className="box-container">
          {[...Array(units)].map((_, index) => {
            const product = products[index];
            const boxColor =
              product?.status === "scanned" ? "#32CD32" : "#007bff";

            return (
              <div
                key={index}
                className="box"
                style={{ backgroundColor: boxColor }}
                onClick={() => handleBoxClick(product)}
              >
                {index + 1}
              </div>
            );
          })}
        </div>
      )}

      {selectedProduct && (
        <>
          <div className="overlay" onClick={() => setSelectedProduct(null)} />
          <div className="product-popup">
            <div className="popup-content">
              {selectedProduct.status === "scanned" ? (
                <div className="image-container">
                  <img src={selectedProduct.image.filePath} alt="Product" />
                  <FaSearchPlus
                    size={30}
                    className="zoom-icon"
                    onClick={() =>
                      handleZoomClick(selectedProduct.image.filePath)
                    }
                  />
                  <p>Position: {selectedProduct.position}</p>
                </div>
              ) : (
                <dev>
                  <p>No data available. </p>
                  <p>
                    Robot is not discovered this yet or there is no package
                    there.
                  </p>
                </dev>
              )}
              <button
                className="close-button"
                onClick={() => setSelectedProduct(null)}
              >
                Close
              </button>
            </div>
          </div>
        </>
      )}

      {zoomedImage && (
        <div className="zoom-modal" onClick={() => setZoomedImage(null)}>
          <img src={zoomedImage} alt="Zoomed Product" />
        </div>
      )}
    </div>
  );
};

export default WarehouseMap;
