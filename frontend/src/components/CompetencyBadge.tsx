import { cn } from "@/lib/utils";

interface CompetencyBadgeProps {
  name: string;
  isActive: boolean;
  onClick: () => void;
}

export const CompetencyBadge = ({ name, isActive, onClick }: CompetencyBadgeProps) => {
  return (
    <button
      onClick={onClick}
      className={cn(
        "px-4 py-2 rounded-lg font-medium transition-all duration-200",
        "hover:bg-matrix-accent hover:text-black",
        isActive
          ? "bg-matrix-accent text-black"
          : "bg-matrix-header text-gray-200"
      )}
    >
      {name}
    </button>
  );
};