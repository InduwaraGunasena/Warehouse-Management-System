import { FaWarehouse } from "react-icons/fa";
import { RiRobot2Fill, RiDashboardFill } from "react-icons/ri";
import { MdAccountCircle, MdBugReport } from "react-icons/md";

const menu = [
  {
    title: "Dashboard",
    icon: <RiDashboardFill />,
    path: "/dashboard",
  },
  {
    title: "Warehouse",
    icon: <FaWarehouse />,
    path: "/warehouse",
  },
  {
    title: "Robot",
    icon: <RiRobot2Fill />,
    path: "/robot",
  },
  {
    title: "Account",
    icon: <MdAccountCircle />,
    childrens: [
      {
        title: "Profile",
        path: "/profile",
      },
      {
        title: "Edit Profile",
        path: "/edit-profile",
      },
    ],
  },
  {
    title: "Report Bug",
    icon: <MdBugReport />,
    path: "/contact-us",
  },
];

export default menu;
