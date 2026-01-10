interface SourceCitationProps {
  sources: string[];
}

export default function SourceCitation({ sources }: SourceCitationProps) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 pt-3 border-t border-gray-200">
      <p className="text-xs text-gray-500 font-medium mb-1">Fuentes consultadas:</p>
      <div className="flex flex-wrap gap-1">
        {sources.map((source, index) => (
          <span
            key={index}
            className="inline-block px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded border border-blue-200"
          >
            {source}
          </span>
        ))}
      </div>
    </div>
  );
}
