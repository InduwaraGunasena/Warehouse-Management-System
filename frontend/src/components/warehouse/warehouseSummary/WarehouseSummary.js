import React, { useEffect, useState } from "react";
import "./WarehouseSummary.scss";
import InfoBox from "../../infoBox/InfoBox";
import { TbCheckbox } from "react-icons/tb";
import { LuPackageSearch } from "react-icons/lu";
import { HiOutlineArchiveBox } from "react-icons/hi2";
import productService from "../../../redux/features/product/productService";

// Icons
const scannedIcon = <TbCheckbox size={30} color="#fff" />;
const productIcon = <HiOutlineArchiveBox size={30} color="#fff" />;
const remainingProductIcon = <LuPackageSearch size={30} color="#fff" />;


const WarehouseSummary = ({ products }) => {
  const [totalUnits, setTotalUnits] = useState(0);
  const [scannedCount, setScannedCount] = useState(0);

  useEffect(() => {
    // Fetch total units
    const fetchWarehouseData = async () => {
      const units = await productService.getWarehouseUnits();
      setTotalUnits(units);
    };
  
  fetchWarehouseData();

    // Calculate scanned products
    const scanned = products.filter(product => product.status === "scanned").length;
    setScannedCount(scanned);
  }, [products]);

  const remainingCount = totalUnits - scannedCount;

  return (
    <div className="warehouse-summary">
      <h3 className="--mt">Warehouse Status</h3>
      <div className="info-summary">
        <InfoBox
          icon={productIcon}
          title={"Total Products"}
          count={totalUnits}
          bgColor="card1"
        />
        <InfoBox
          icon={scannedIcon}
          title={"Scanned products"}
          count={scannedCount}
          bgColor="card2"
        />
        <InfoBox
          icon={remainingProductIcon}
          title={"Remaining products"}
          count={remainingCount}
          bgColor="card3"
        />
      </div>
    </div>
  );
};

export default WarehouseSummary;
