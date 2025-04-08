
import { User, BookOpen, LayoutGrid, List } from "lucide-react";
import { Link } from "react-router-dom";

const TopMenu = () => {
  return (
    <nav className="w-full bg-matrix-header py-4 px-6 sticky top-0 z-50">
      <div className="max-w-[1920px] mx-auto flex items-center justify-between">
        <Link to="/" className="text-matrix-accent font-bold text-xl min-w-[100px]">МКИ</Link>
        
        <div className="flex items-center justify-center space-x-6 flex-grow px-4">
          <Link 
            to="/about" 
            className="flex items-center gap-2 text-gray-300 hover:text-matrix-accent transition-colors whitespace-nowrap"
          >
            <User className="h-4 w-4" />
            <span>Обо мне</span>
          </Link>
          
          <Link 
            to="/blog" 
            className="flex items-center gap-2 text-gray-300 hover:text-matrix-accent transition-colors whitespace-nowrap"
          >
            <BookOpen className="h-4 w-4" />
            <span>Блог</span>
          </Link>
          
          <Link 
            to="/" 
            className="flex items-center gap-2 text-gray-300 hover:text-matrix-accent transition-colors whitespace-nowrap"
          >
            <LayoutGrid className="h-4 w-4" />
            <span>Матрица компетенций</span>
          </Link>
          
          <Link 
            to="/watchlist" 
            className="flex items-center gap-2 text-gray-300 hover:text-matrix-accent transition-colors whitespace-nowrap"
          >
            <List className="h-4 w-4" />
            <span>Список наблюдения</span>
          </Link>
        </div>

        <div className="min-w-[100px]"></div>
      </div>
    </nav>
  );
};

export default TopMenu;
