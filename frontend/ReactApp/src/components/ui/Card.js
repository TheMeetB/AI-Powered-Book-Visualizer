export function Card({ children }) {
  return (
    <div className="card">
      {children}
    </div>
  );
}

export function CardContent({ image, title, description, actions }) {
  return (
    <div className="card-content">
      {image && <img src={image} alt={title} className="card-image" />}
      <h3 className="card-title">{title}</h3>
      <p className="card-description">{description}</p>
      <div className="card-actions">
        {actions}
      </div>
    </div>
  );
}
