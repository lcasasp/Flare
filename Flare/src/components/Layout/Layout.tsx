import React, { useEffect, useState } from "react";
import { fetchData, searchArticles } from "../../api";
import Articles from "./articles";
import Header from "./Header/Header";
import Footer from "./Footer/Footer";

interface Article {
  id: number;
  title: string;
  content: string;
  url: string;
}

const Layout: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [articles, setArticles] = useState<Article[]>([]);

  useEffect(() => {
    console.log("useEffect triggered");
    const fetchArticlesData = async () => {
      try {
        const response = await fetchData();
        const articlesData = response?.news.filter(
          (article: { title: null; content: null }) =>
            article.title !== null && article.content !== null
        ); // Filter articles with non-null title and content
        setArticles(articlesData);
      } catch (error) {
        console.error("Error fetching articles:", error);
      }
    };

    fetchArticlesData();
  }, []);

  const handleSearch = async () => {
    try {
      const response = await searchArticles(searchTerm); // Use the fetchData function from api.ts
      console.log(response);
      const articlesData = response?.news.filter(
        (article: { title: null; content: null }) =>
          article.title !== null && article.content !== null
      ); // Filter articles with non-null title and content
      setArticles(articlesData);
    } catch (error) {
      console.error("Error querying articles:", error);
    }
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
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Enter search term"
          style={{
            padding: '10px',
            border: '1px solid green',
            borderRadius: '4px',
            marginRight: '10px',
            width: '300px', // Adjust the width as per your preference
          }}
        />
        <button
          onClick={handleSearch}
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
