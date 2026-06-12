import { cn } from "../../utils/cn";

function Card({ children, className = "", as: Component = "div", ...props }) {
  return (
    <Component className={cn("card-base", className)} {...props}>
      {children}
    </Component>
  );
}

export default Card;
