
import { Github, Twitter, Linkedin, Heart } from "lucide-react";
import { Button } from "./ui/button";

const Footer = () => {
  return (
    <footer className="w-full bg-matrix-header mt-auto py-8 px-4">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* About Section */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-200">О проекте</h3>
          <p className="text-gray-400 text-sm">
            Помогаем разработчикам расти через всесторонние матрицы компетенций и учебные ресурсы.
          </p>
        </div>

        {/* Quick Links */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-200">Быстрые ссылки</h3>
          <ul className="space-y-2">
            <li>
              <a href="#" className="text-gray-400 hover:text-matrix-accent text-sm">
                Документация
              </a>
            </li>
            <li>
              <a href="#" className="text-gray-400 hover:text-matrix-accent text-sm">
                Ресурсы
              </a>
            </li>
            <li>
              <a href="#" className="text-gray-400 hover:text-matrix-accent text-sm">
                Блог
              </a>
            </li>
          </ul>
        </div>

        {/* Connect */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-200">Связаться</h3>
          <div className="flex space-x-4">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-matrix-accent"
            >
              <Github className="h-5 w-5" />
            </a>
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-matrix-accent"
            >
              <Twitter className="h-5 w-5" />
            </a>
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-matrix-accent"
            >
              <Linkedin className="h-5 w-5" />
            </a>
          </div>
        </div>

        {/* Support */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-200">Поддержать проект</h3>
          <p className="text-gray-400 text-sm">
            Помогите нам сохранить этот ресурс бесплатным и актуальным
          </p>
          <Button
            variant="outline"
            className="flex items-center gap-2 bg-matrix-accent text-white hover:bg-matrix-accent-dark"
            onClick={() => window.open('https://github.com/sponsors', '_blank')}
          >
            <Heart className="h-4 w-4" /> Пожертвовать
          </Button>
        </div>
      </div>

      {/* Copyright */}
      <div className="mt-8 pt-8 border-t border-matrix-border">
        <p className="text-center text-gray-400 text-sm">
          © {new Date().getFullYear()} Исследователь матрицы компетенций. Все права защищены.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
