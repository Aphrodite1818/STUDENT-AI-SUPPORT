/** CARD COMPONENT **/



/**
 * Reusable content container with the project's default card styling.
 *
 * Use this component to group related UI content such as dashboard stats,
 * forms, summaries, or list sections. It applies the shared `card-base`
 * Tailwind component class and allows extra utility classes through
 * `className`.
 *
 * @param {object} props - Card component props.
 * @param {import("react").ReactNode} props.children - Content rendered inside the card.
 * @param {string} [props.className=""] - Additional Tailwind or custom classes appended to the base card styles.
 * @returns {JSX.Element} A styled card container.
 */
function Card({ children, className = "" }) {
  return <div className={`card-base ${className}`}>{children}</div>;
}

export default Card;
