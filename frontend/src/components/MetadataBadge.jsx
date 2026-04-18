const BADGE_COLORS = [
  'bg-blue-100 text-blue-800',
  'bg-purple-100 text-purple-800',
  'bg-green-100 text-green-800',
  'bg-red-100 text-red-800',
];

export default function MetadataBadge({ label, value, colorIndex }) {
  const colorClass = BADGE_COLORS[colorIndex % 4];

  return (
    <span className={`inline-block px-2 rounded-full text-[11px] ${colorClass}`}>
      {label}: {value}
    </span>
  );
}
