export default function EmptyState({ message = 'No data found yet.' }) {
  return <p className="state-message">{message}</p>;
}

