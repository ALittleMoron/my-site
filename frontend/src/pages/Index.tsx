import { CompetencyMatrix } from "@/components/CompetencyMatrix";
import Footer from "@/components/Footer";
import TopMenu from "@/components/TopMenu";

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <TopMenu />
      <main className="flex-grow">
        <CompetencyMatrix />
      </main>
      <Footer />
    </div>
  );
};

export default Index;