import React, { useEffect, useState } from "react";
import { searchArticles } from "../../api";
import Articles from "./articles";
import Header from "./Header/Header";
import Footer from "./Footer/Footer";

interface Article {
  id: number;
  title: string;
  content: string;
  url: string;
  published_at: string
}

const Layout: React.FC = () => {
  const [inputValue, setInputValue] = useState("");
  const [searchTerm, setSearchTerm] = useState("Energy Climate");
  const [articles, setArticles] = useState<Article[]>([]);

  useEffect(() => {
    handleSearch();
  }, [searchTerm]);

  const handleSearch = async () => {
    try {
      const response = await searchArticles(searchTerm);
      console.log("Succesfully queried for: " + searchTerm);
      const articlesData = response?.news.filter(
        (article: { title: null; content: null }) =>
          article.title !== null && article.content !== null
      );
      setArticles(articlesData);
    } catch (error) {
      console.error("Error querying articles:", error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleButtonClick = () => {
    setSearchTerm(inputValue);
  };

  return (
    <div>
      <Header />
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          marginBottom: "20px",
        }}
      >
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          placeholder="Enter search term"
          style={{
            padding: '10px',
            border: '1px solid green',
            borderRadius: '4px',
            marginRight: '10px',
            width: '300px',
          }}
        />
        <button
          onClick={handleButtonClick}
          style={{
            padding: "10px 20px",
            backgroundColor: "green",
            color: "white",
            border: "none",
            borderRadius: "4px",
          }}
        >
          Search
        </button>
      </div>
      <Articles articles={articles} />
      <Footer />
    </div>
  );
};

export default Layout;