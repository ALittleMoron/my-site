import { api } from "@/services/api";
import { useEffect, useState } from "react";
import { CompetencyTable } from "./CompetencyTable";

export const CompetencyMatrix = () => {
  const [sheets, setSheets] = useState<string[]>([]);
  const [selectedSheet, setSelectedSheet] = useState<string>("");
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('CompetencyMatrix component mounted');

    const fetchSheets = async () => {
      try {
        console.log('Starting to fetch sheets...');
        setIsLoading(true);
        setError(null);
        
        const response = await api.getSheets();
        console.log('Sheets response:', response);
        
        if (!response || !response.sheets) {
          throw new Error('Invalid response format from API');
        }
        
        setSheets(response.sheets);
        if (response.sheets.length > 0) {
          setSelectedSheet(response.sheets[0]);
        } else {
          console.warn('No sheets available in the response');
        }
      } catch (error) {
        console.error('Error fetching sheets:', error);
        setError(error instanceof Error ? error.message : 'Failed to load sheets. Please check the console for details.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSheets();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-gray-100">Loading sheets...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-matrix-header rounded-lg border border-matrix-border p-6 max-w-2xl mx-auto">
        <h3 className="text-xl font-bold text-gray-100 mb-2">Error loading competency matrix</h3>
        <p className="text-gray-300 mb-2">{error}</p>
        <p className="text-gray-400 text-sm">Please check the browser console for more details.</p>
      </div>
    );
  }

  if (sheets.length === 0) {
    return (
      <div className="bg-matrix-header rounded-lg border border-matrix-border p-6 max-w-2xl mx-auto">
        <div className="text-gray-100">No sheets available</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-matrix-bg p-8">
      <h1 className="text-3xl font-bold text-gray-100 mb-8">Матрица компетенций</h1>
      
      <div className="space-y-4">
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
          <select
            value={selectedSheet}
            onChange={(e) => setSelectedSheet(e.target.value)}
            className="bg-matrix-bg border border-matrix-border text-gray-100 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-matrix-accent min-w-[200px]"
          >
            {sheets.map((sheet) => (
              <option key={sheet} value={sheet}>
                {sheet}
              </option>
            ))}
          </select>

          <div className="flex gap-2">
            <button
              onClick={() => setViewMode("list")}
              className={`px-4 py-2 rounded ${
                viewMode === "list"
                  ? "bg-matrix-accent text-gray-100"
                  : "bg-matrix-bg/30 text-gray-300 hover:bg-matrix-bg/50"
              }`}
            >
              List View
            </button>
            <button
              onClick={() => setViewMode("grid")}
              className={`px-4 py-2 rounded ${
                viewMode === "grid"
                  ? "bg-matrix-accent text-gray-100"
                  : "bg-matrix-bg/30 text-gray-300 hover:bg-matrix-bg/50"
              }`}
            >
              Grid View
            </button>
          </div>
        </div>

        <CompetencyTable sheetName={selectedSheet} viewMode={viewMode} />
      </div>
    </div>
  );
};
