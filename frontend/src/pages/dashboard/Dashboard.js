import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import WarehouseMap from "../../components/warehouse/warehouseMap/WarehouseMap";
import WarehouseSummary from "../../components/warehouse/warehouseSummary/WarehouseSummary";

import useRedirectLoggedOutUser from "../../customHook/useRedirectLoggedOutUser";
import { selectIsLoggedIn } from "../../redux/features/auth/authSlice";
import { getProducts } from "../../redux/features/product/productSlice";

const Dashboard = () => {
  useRedirectLoggedOutUser("/login");
  const dispatch = useDispatch();

  const isLoggedIn = useSelector(selectIsLoggedIn);
  const { products, isLoading, isError, message } = useSelector(
    (state) => state.product
  );

  useEffect(() => {
    if (isLoggedIn === true) {
      dispatch(getProducts());
    }

    if (isError) {
      console.log(message);
    }
  }, [isLoggedIn, isError, message, dispatch]);

  return (
    <div>
      <WarehouseSummary products={products} />
      <WarehouseMap products={products} isLoading={isLoading} />
    </div>
  );
};

export default Dashboard;
