
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import { useState } from "react";
import { useIsMobile } from "@/hooks/use-mobile";

interface Question {
  text: string;
  answer?: string;
  resources?: string[];
}

interface Subsection {
  name: string;
  content: {
    [key: string]: Question[];
  };
}

interface CompetencyTableProps {
  data: {
    section: string;
    subsections: Subsection[];
  }[];
  viewMode: "list" | "grid";
}

export const CompetencyTable = ({ data, viewMode }: CompetencyTableProps) => {
  const grades = ["Junior", "Junior+", "Middle", "Middle+", "Senior"];
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const isMobile = useIsMobile();

  if (viewMode === "list") {
    return (
      <>
        <div className="space-y-6">
          {data.map((sectionData, sectionIndex) => (
            <div key={`section-${sectionIndex}`} className="bg-matrix-header rounded-lg border border-matrix-border p-4">
              <h2 className="text-xl font-bold text-gray-100 mb-4">{sectionData.section}</h2>
              
              <div className="space-y-6">
                {sectionData.subsections.map((subsection, subIndex) => (
                  <div key={`${sectionData.section}-${subsection.name}-${subIndex}`} className="border-t border-matrix-border pt-4 first:border-t-0 first:pt-0">
                    <h3 className="text-lg font-medium text-gray-100 mb-3">{subsection.name}</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                      {grades.map((grade) => (
                        <div key={grade} className="bg-matrix-bg/30 p-3 rounded">
                          <div className="text-gray-300 text-sm font-medium mb-2">{grade}</div>
                          <div className="space-y-2">
                            {subsection.content[grade]?.map((question, qIndex) => (
                              <div
                                key={qIndex}
                                onClick={() => setSelectedQuestion(question)}
                                className="text-matrix-accent hover:text-matrix-accent-dark cursor-pointer transition-colors text-sm break-words"
                              >
                                {question.text}
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
                <p className="break-words">{selectedQuestion?.text}</p>
              </div>
              {selectedQuestion?.answer && (
                <div className="text-gray-100">
                  <h3 className="font-semibold mb-2">Ответ:</h3>
                  <p className="break-words whitespace-pre-wrap">{selectedQuestion.answer}</p>
                </div>
              )}
              {selectedQuestion?.resources && selectedQuestion.resources.length > 0 && (
                <div className="text-gray-100">
                  <h3 className="font-semibold mb-2">Ресурсы:</h3>
                  <ul className="list-disc pl-5">
                    {selectedQuestion.resources.map((resource, index) => (
                      <li key={index} className="text-matrix-accent break-all">
                        <a href={resource} target="_blank" rel="noopener noreferrer">
                          {resource}
                        </a>
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
              {grades.map((grade) => (
                <th key={grade} className="p-4 text-left text-gray-100 border-b border-matrix-border">
                  {grade}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((sectionData) => (
              sectionData.subsections.map((subsection, subIndex) => (
                <tr key={`${sectionData.section}-${subIndex}`} className="border-b border-matrix-border">
                  {subIndex === 0 ? (
                    <td rowSpan={sectionData.subsections.length} className="p-4 border-r border-matrix-border text-gray-100">
                      {sectionData.section}
                    </td>
                  ) : null}
                  <td className="p-4 border-r border-matrix-border text-gray-100">
                    {subsection.name}
                  </td>
                  {grades.map((grade) => (
                    <td key={grade} className="p-4 border-r border-matrix-border">
                      <div className="space-y-2">
                        {subsection.content[grade]?.map((question, qIndex) => (
                          <div
                            key={qIndex}
                            onClick={() => setSelectedQuestion(question)}
                            className="text-matrix-accent hover:text-matrix-accent-dark cursor-pointer transition-colors break-words"
                          >
                            {question.text}
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
              <p className="break-words">{selectedQuestion?.text}</p>
            </div>
            {selectedQuestion?.answer && (
              <div className="text-gray-100">
                <h3 className="font-semibold mb-2">Ответ:</h3>
                <p className="break-words whitespace-pre-wrap">{selectedQuestion.answer}</p>
              </div>
            )}
            {selectedQuestion?.resources && selectedQuestion.resources.length > 0 && (
              <div className="text-gray-100">
                <h3 className="font-semibold mb-2">Ресурсы:</h3>
                <ul className="list-disc pl-5">
                  {selectedQuestion.resources.map((resource, index) => (
                    <li key={index} className="text-matrix-accent break-all">
                      <a href={resource} target="_blank" rel="noopener noreferrer">
                        {resource}
                      </a>
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
