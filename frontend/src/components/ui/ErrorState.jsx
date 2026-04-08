export default function ErrorState({ message, onRetry }) {
  return (
    <div className="error-state">
      <p className="error-text">{message || 'Something failed. Please try again.'}</p>
      {onRetry ? (
        <button className="secondary-button" type="button" onClick={onRetry}>
          Try Again
        </button>
      ) : null}
    </div>
  );
}

