import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import { useEffect, useState } from "react";
import { useIsMobile } from "@/hooks/use-mobile";
import { api, CompetencyMatrixItem, CompetencyMatrixItemsResponse } from "@/services/api";

interface CompetencyTableProps {
  sheetName: string;
  viewMode: "list" | "grid";
}

export const CompetencyTable = ({ sheetName, viewMode }: CompetencyTableProps) => {
  const [data, setData] = useState<CompetencyMatrixItemsResponse | null>(null);
  const [selectedQuestion, setSelectedQuestion] = useState<CompetencyMatrixItem | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const isMobile = useIsMobile();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const response = await api.getItems(sheetName);
        setData(response);
      } catch (error) {
        console.error('Error fetching competency matrix data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [sheetName]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-gray-100">Loading data...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-matrix-header rounded-lg border border-matrix-border p-6 max-w-2xl mx-auto">
        <div className="text-gray-100">No data available</div>
      </div>
    );
  }

  if (viewMode === "list") {
    return (
      <>
        <div className="space-y-6">
          {data.sections.map((sectionData, sectionIndex) => (
            <div key={`section-${sectionIndex}`} className="bg-matrix-header rounded-lg border border-matrix-border p-4">
              <h2 className="text-xl font-bold text-gray-100 mb-4">{sectionData.section}</h2>
              
              <div className="space-y-6">
                {sectionData.subsections.map((subsection, subIndex) => (
                  <div key={`${sectionData.section}-${subsection.subsection}-${subIndex}`} className="border-t border-matrix-border pt-4 first:border-t-0 first:pt-0">
                    <h3 className="text-lg font-medium text-gray-100 mb-3">{subsection.subsection}</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                      {subsection.grades.map((gradeData) => (
                        <div key={gradeData.grade} className="bg-matrix-bg/30 p-3 rounded">
                          <div className="text-gray-300 text-sm font-medium mb-2">{gradeData.grade}</div>
                          <div className="space-y-2">
                            {gradeData.items.map((question) => (
                              <div
                                key={question.id}
                                onClick={() => setSelectedQuestion(question)}
                                className="text-matrix-accent hover:text-matrix-accent-dark cursor-pointer transition-colors text-sm break-words"
                              >
                                {question.question}
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <AlertDialog open={!!selectedQuestion} onOpenChange={() => setSelectedQuestion(null)}>
          <AlertDialogContent className="bg-matrix-bg border-matrix-border max-w-[90vw] md:max-w-[800px] w-full overflow-y-auto max-h-[90vh]">
            <AlertDialogHeader>
              <AlertDialogTitle className="text-gray-100">Детали вопроса</AlertDialogTitle>
            </AlertDialogHeader>
            <div className="space-y-4">
              <div className="text-gray-100">
                <h3 className="font-semibold mb-2">Вопрос:</h3>
                <p className="break-words">{selectedQuestion?.question}</p>
              </div>
              {selectedQuestion?.answer && (
                <div className="text-gray-100">
                  <h3 className="font-semibold mb-2">Ответ:</h3>
                  <p className="break-words whitespace-pre-wrap">{selectedQuestion.answer}</p>
                </div>
              )}
              {selectedQuestion?.interviewExpectedAnswer && (
                <div className="text-gray-100">
                  <h3 className="font-semibold mb-2">Ожидаемый ответ:</h3>
                  <p className="break-words whitespace-pre-wrap">{selectedQuestion.interviewExpectedAnswer}</p>
                </div>
              )}
              {selectedQuestion?.resources && selectedQuestion.resources.length > 0 && (
                <div className="text-gray-100">
                  <h3 className="font-semibold mb-2">Ресурсы:</h3>
                  <ul className="list-disc pl-5">
                    {selectedQuestion.resources.map((resource) => (
                      <li key={resource.id} className="text-matrix-accent break-all">
                        <a href={resource.url} target="_blank" rel="noopener noreferrer">
                          {resource.name}
                        </a>
                        {resource.context && <p className="text-gray-400 text-sm mt-1">{resource.context}</p>}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </AlertDialogContent>
        </AlertDialog>
      </>
    );
  }

  // Grid view (now using a table)
  return (
    <>
      <div className="overflow-x-auto rounded-lg border border-matrix-border">
        <table className="w-full border-collapse">
          <thead className="bg-matrix-header">
            <tr>
              <th className={`${isMobile ? 'w-1/4' : 'w-1/6'} p-4 text-left text-gray-100 border-b border-matrix-border`}>Раздел</th>
              <th className={`${isMobile ? 'w-1/4' : 'w-1/6'} p-4 text-left text-gray-100 border-b border-matrix-border border-r border-matrix-border`}>Подраздел</th>
              {data.sections[0]?.subsections[0]?.grades.map((grade) => (
                <th key={grade.grade} className="p-4 text-left text-gray-100 border-b border-matrix-border">
                  {grade.grade}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.sections.map((sectionData) => (
              sectionData.subsections.map((subsection, subIndex) => (
                <tr key={`${sectionData.section}-${subIndex}`} className="border-b border-matrix-border">
                  {subIndex === 0 ? (
                    <td rowSpan={sectionData.subsections.length} className="p-4 border-r border-matrix-border text-gray-100">
                      {sectionData.section}
                    </td>
                  ) : null}
                  <td className="p-4 border-r border-matrix-border text-gray-100">
                    {subsection.subsection}
                  </td>
                  {subsection.grades.map((grade) => (
                    <td key={grade.grade} className="p-4 border-r border-matrix-border">
                      <div className="space-y-2">
                        {grade.items.map((question) => (
                          <div
                            key={question.id}
                            onClick={() => setSelectedQuestion(question)}
                            className="text-matrix-accent hover:text-matrix-accent-dark cursor-pointer transition-colors break-words"
                          >
                            {question.question}
                          </div>
                        ))}
                      </div>
                    </td>
                  ))}
                </tr>
              ))
            ))}
          </tbody>
        </table>
      </div>

      <AlertDialog open={!!selectedQuestion} onOpenChange={() => setSelectedQuestion(null)}>
        <AlertDialogContent className="bg-matrix-bg border-matrix-border max-w-[90vw] md:max-w-[800px] w-full overflow-y-auto max-h-[90vh]">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-gray-100">Детали вопроса</AlertDialogTitle>
          </AlertDialogHeader>
          <div className="space-y-4">
            <div className="text-gray-100">
              <h3 className="font-semibold mb-2">Вопрос:</h3>
              <p className="break-words">{selectedQuestion?.question}</p>
            </div>
            {selectedQuestion?.answer && (
              <div className="text-gray-100">
                <h3 className="font-semibold mb-2">Ответ:</h3>
                <p className="break-words whitespace-pre-wrap">{selectedQuestion.answer}</p>
              </div>
            )}
            {selectedQuestion?.interviewExpectedAnswer && (
              <div className="text-gray-100">
                <h3 className="font-semibold mb-2">Ожидаемый ответ:</h3>
                <p className="break-words whitespace-pre-wrap">{selectedQuestion.interviewExpectedAnswer}</p>
              </div>
            )}
            {selectedQuestion?.resources && selectedQuestion.resources.length > 0 && (
              <div className="text-gray-100">
                <h3 className="font-semibold mb-2">Ресурсы:</h3>
                <ul className="list-disc pl-5">
                  {selectedQuestion.resources.map((resource) => (
                    <li key={resource.id} className="text-matrix-accent break-all">
                      <a href={resource.url} target="_blank" rel="noopener noreferrer">
                        {resource.name}
                      </a>
                      {resource.context && <p className="text-gray-400 text-sm mt-1">{resource.context}</p>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};
