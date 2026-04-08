import React, { useEffect, useState, useCallback } from "react";
import { GlobalWorkerOptions } from "pdfjs-dist";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import "./Dashboard.css";
import api from "../../api";
import { FiBookOpen } from "react-icons/fi";
import { AiFillDelete } from "react-icons/ai";
import {
    FaBars,
    FaBell,
    FaBookmark,
    FaHeart,
    FaHome,
    FaPlus,
    FaSearch,
    FaSignOutAlt,
    FaTimes,
    FaBookReader
} from "react-icons/fa";
import FlipBook from "./FlipBook";

const Dashboard = () => {
    const storedToken = sessionStorage.getItem("accessToken");
    const storedUserid = sessionStorage.getItem("userId");
    const storedUsername = sessionStorage.getItem("userName");

    const [notifications, setNotifications] = useState([]);
    const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
    const [books, setBooks] = useState([]);
    const [bookType, setBookType] = useState([]);
    const [selectedBook, setSelectedBook] = useState(null);
    const [bookDataUrl, setbookDataUrl] = useState(null);
    const [favorites, setFavorites] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const [toBeRead, setToBeRead] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isProfileOpen, setIsProfileOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const navigate = useNavigate();
    const [selectedGenerationType, setSelectedGenerationType] = useState(null);
    const [bookmarks, setBookmarks] = useState([]);
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [activeSection, setActiveSection] = useState("dashboard");

    GlobalWorkerOptions.workerSrc = `${window.location.origin}/pdf.worker.min.mjs`;

    const fetchBooks = useCallback(async () => {
        try {
            const response = await api.get(`dashboard/get_all_books/${storedUserid}`, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${storedToken}`
                }
            });
            setBooks(response.data.data);
        } catch (error) {
            console.error("Error getting book:", error);
        }
    }, [storedUserid, storedToken]);

    useEffect(() => {
        fetchBooks();
        // Default to dark theme for the kinetic vibe
        document.documentElement.setAttribute('data-theme', 'dark');
    }, [fetchBooks]);

    const toggleNotifications = () => {
        setIsNotificationsOpen(!isNotificationsOpen);
        if (isProfileOpen) setIsProfileOpen(false);
    };

    const logout = () => {
        localStorage.clear();
        sessionStorage.clear();
        navigate("/");
    };

    const handleUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("data", file);
        formData.append("user_id", storedUserid);

        const tempBookId = `temp-${Date.now()}`;

        setBooks((prevBooks) => [
            ...prevBooks,
            { book_id: tempBookId, title: file.name, uploading: true, progress: 0 }
        ]);

        setNotifications((prev) => [
            ...prev,
            { id: tempBookId, message: `Uploading ${file.name}...`, type: "info" }
        ]);

        const waitForBookReady = async (bookId) => {
            const maxAttempts = 10;
            let attempts = 0;
            while (attempts < maxAttempts) {
                try {
                    const response = await api.get(`dashboard/get_all_books/${storedUserid}`, {
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${storedToken}`
                        }
                    });
                    const allBooks = response.data.data;
                    const foundBook = allBooks.find((book) => book.book_id === bookId);
                    if (foundBook) {
                        return foundBook;
                    }
                } catch (err) { }
                await new Promise((resolve) => setTimeout(resolve, 1000));
                attempts++;
            }
            throw new Error("Book not ready after polling.");
        };

        try {
            const response = await api.post("dashboard/insert_book", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                    Authorization: `Bearer ${storedToken}`
                },
                onUploadProgress: (progressEvent) => {
                    const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setBooks((prevBooks) =>
                        prevBooks.map((book) =>
                            book.book_id === tempBookId ? { ...book, progress: percent } : book
                        )
                    );
                }
            });

            const uploadedBookId = response.data.data.book_id;
            const uploadedBook = await waitForBookReady(uploadedBookId);

            setBooks((prevBooks) => {
                const updatedBooks = prevBooks.filter(book => book.book_id !== tempBookId);
                return [{ ...uploadedBook, uploading: false }, ...updatedBooks];
            });

            setNotifications((prev) =>
                prev.filter((notif) => notif.id !== tempBookId).concat({
                    id: uploadedBook.book_id, message: `${file.name} uploaded successfully!`, type: "success"
                })
            );
        } catch (error) {
            setBooks((prevBooks) => prevBooks.filter((book) => book.book_id !== tempBookId));
            setNotifications((prev) =>
                prev.filter((notif) => notif.id !== tempBookId).concat({
                    id: Date.now(), message: `Failed to upload ${file.name}`, type: "error"
                })
            );
        }
    };

    const openModal = async (book) => {
        setSelectedBook(book);
        try {
            const response = await api.get(`dashboard/get_book_data/${book.book_id}`, {
                responseType: 'blob',
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${storedToken}`
                }
            });
            const book_data_url = URL.createObjectURL(response.data);
            setbookDataUrl(book_data_url);
            if (response.data.type === "application/pdf") {
                setBookType("pdf");
            } else if (response.data.type === "application/epub+zip") {
                setBookType("epub");
            }
        } catch (error) {
            console.error("Error Failed opening book:", error);
        }
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setSelectedBook(null);
    };

    const deleteBook = async (bookId) => {
        try {
            await api.delete(`dashboard/${bookId}/delete`, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${storedToken}`
                }
            });
            setBooks(prevBooks => prevBooks.filter(book => book.book_id !== bookId));
        } catch (error) { }
    };

    const addLike = async (bookId) => {
        try {
            await api.post(`dashboard/${bookId}/like, {book_id: bookId}`, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: ` Bearer ${storedToken}`
                }
            });
        } catch (error) { }
        await fetchBooks();
        setFavorites(prev =>
            prev.some(book => book.book_id === bookId)
                ? prev.filter(book => book.book_id !== bookId)
                : [...prev, books.find(book => book.book_id === bookId)]
        );
    };

    const toggleBookmark = async (bookId) => {
        try {
            await api.post(`dashboard/${bookId}/bookmark, {book_id: bookId}`, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${storedToken}`
                }
            });
        } catch (error) { }
        await fetchBooks();
        setBookmarks(prev =>
            prev.includes(bookId) ? prev.filter(id => id !== bookId) : [...prev, bookId]
        );
        setToBeRead(prev =>
            prev.some(book => book.book_id === bookId)
                ? prev.filter(book => book.book_id !== bookId)
                : [...prev, books.find(book => book.book_id === bookId)]
        );
    };

    const handleGenerate = (type, bookId) => {
        setSelectedGenerationType(type);
        navigate('/ai', { state: { fromApp: true, bookId } });
    };

    const handleDragEnter = (e) => { e.preventDefault(); setIsDragging(true); };
    const handleDragLeave = (e) => { e.preventDefault(); setIsDragging(false); };
    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files.length > 0) {
            handleUpload({ target: { files: e.dataTransfer.files } });
        }
    };

    const getFilteredBooks = (bookList) => {
        return bookList.filter(book => book.title?.toLowerCase().includes(searchQuery.toLowerCase()));
    };

    return (
        <div className="dashboard-container">
            {/* Sidebar */}
            <aside className={`sidebar ${!isSidebarOpen ? "hidden" : ""}`}>
                <div className="sidebar-header">
                    <div className="sidebar-brand" onClick={() => navigate("/")}>
                        <FiBookOpen /> <span>Book Visualizer</span>
                    </div>
                </div>
                <div className="sidebar-nav">
                    <button className={`nav-item ${activeSection === "dashboard" ? "active" : ""}`} onClick={() => setActiveSection("dashboard")}>
                        <FaHome size={18} /> Library
                    </button>
                    <button className={`nav-item ${activeSection === "favorites" ? "active" : ""}`} onClick={() => setActiveSection("favorites")}>
                        <FaHeart size={18} /> Favorites
                    </button>
                    <button className={`nav-item ${activeSection === "toBeRead" ? "active" : ""}`} onClick={() => setActiveSection("toBeRead")}>
                        <FaBookmark size={18} /> To Read
                    </button>
                </div>
                <div className="sidebar-footer">
                    <button className="logout-btn" onClick={logout}>
                        <FaSignOutAlt /> Sign Out
                    </button>
                </div>
            </aside>

            {/* Main Content Areas */}
            <main className="main-content">
                <header className="dashboard-header">
                    <div className="header-left">
                        <button className="toggle-sidebar-btn" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
                            {isSidebarOpen ? <FaTimes /> : <FaBars />}
                        </button>
                        <div className="search-bar">
                            <FaSearch className="search-icon" />
                            <input
                                type="text"
                                placeholder="Search library..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                    </div>
                    <div className="header-right">
                        <button className="icon-btn" onClick={toggleNotifications}>
                            <FaBell />
                            {notifications.length > 0 && <span className="notification-badge"></span>}
                        </button>

                        <div className="user-profile">
                            <div className="avatar">
                                {storedUsername ? storedUsername.charAt(0).toUpperCase() : "U"}
                            </div>
                            <div className="user-info">
                                <span className="user-name">{storedUsername}</span>
                                <span className="user-role">Scholar</span>
                            </div>
                        </div>
                    </div>
                </header>

                <div className="workspace">
                    <div className="workspace-header">
                        <div className="workspace-title">
                            <h1>
                                {activeSection === "dashboard" && "Main Library"}
                                {activeSection === "favorites" && "Favorite Texts"}
                                {activeSection === "toBeRead" && "Reading Queue"}
                            </h1>
                            <p>Manage and immerse yourself in your digital collection.</p>
                        </div>
                        {activeSection === "dashboard" && (
                            <button className="upload-btn" onClick={() => document.getElementById("file-upload").click()}>
                                Upload Document
                            </button>
                        )}
                    </div>

                    {activeSection === "dashboard" && (
                        <label
                            className={`upload-area ${isDragging ? 'drag-active' : ''}`}
                            onDragEnter={handleDragEnter}
                            onDragOver={handleDragEnter}
                            onDragLeave={handleDragLeave}
                            onDrop={handleDrop}
                            htmlFor="file-upload"
                        >
                            <div className="upload-icon-wrapper">
                                <FaPlus size={24} />
                            </div>
                            <h3>Drag & Drop Documents</h3>
                            <p>Supports PDF, EPUB, and TEXT files. AI analysis will begin automatically.</p>
                            <span className="browse-btn">Browse Files</span>
                            <input id="file-upload" type="file" onChange={handleUpload} hidden />
                        </label>
                    )}

                    {books.some(b => b.uploading) && (
                        <div className="upload-progress-container">
                            {books.filter(b => b.uploading).map(book => (
                                <div key={book.book_id}>
                                    <div className="upload-status">
                                        <span>Archiving "{book.title}"...</span>
                                        <span>{book.progress}%</span>
                                    </div>
                                    <div className="progress-bar-bg">
                                        <div className="progress-bar-fill" style={{ width: `${book.progress}%` }}></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="books-grid">
                        <AnimatePresence>
                            {getFilteredBooks(activeSection === "dashboard" ? books : activeSection === "favorites" ? favorites : toBeRead).filter(b => !b.uploading).map((book, i) => (
                                <motion.div
                                    key={book.book_id}
                                    className="book-card"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    transition={{ delay: i * 0.05 }}
                                >
                                    <div className="card-image-container">
                                        <div className="status-badge processed">Archived</div>
                                        {book.book_cover ? (
                                            <img src={book.book_cover} alt={book.title} style={{ width: '100%', height: '100%', objectFit: 'cover', position: 'absolute', inset: 0 }} />
                                        ) : (
                                            <div className="book-cover-placeholder">
                                                <FiBookOpen size={30} />
                                            </div>
                                        )}
                                    </div>
                                    <div className="card-content">
                                        <h3 className="book-title">{book.title}</h3>
                                        <div className="book-meta">
                                            <span>Volume {i + 1}</span>
                                            <span>Text</span>
                                        </div>
                                        <div className="card-actions">
                                            <button className="action-btn view-btn" onClick={() => openModal(book)}>
                                                Read
                                            </button>
                                            <button
                                                className="action-btn icon-action-btn"
                                                onClick={() => toggleBookmark(book.book_id)}
                                                style={{ color: bookmarks.includes(book.book_id) ? 'var(--lib-accent)' : '' }}
                                            >
                                                <FaBookmark />
                                            </button>
                                            <button
                                                className="action-btn icon-action-btn"
                                                onClick={() => addLike(book.book_id)}
                                                style={{ color: favorites.some(b => b.book_id === book.book_id) ? '#EF4444' : '' }}
                                            >
                                                <FaHeart />
                                            </button>
                                            <button className="action-btn icon-action-btn delete" onClick={() => deleteBook(book.book_id)}>
                                                <AiFillDelete />
                                            </button>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        {getFilteredBooks(activeSection === "dashboard" ? books : activeSection === "favorites" ? favorites : toBeRead).filter(b => !b.uploading).length === 0 && (
                            <div className="empty-state" style={{ gridColumn: '1 / -1' }}>
                                <div className="empty-icon">
                                    <FiBookOpen size={32} />
                                </div>
                                <h3>The Archives Are Empty</h3>
                                <p>There are no texts matching your current criteria. Upload a new document to begin your reading journey.</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>

            {/* Modal / Book Viewer */}
            {isModalOpen && selectedBook && (
                <div className="modal-overlay">
                    <motion.div
                        className="modal-content animate-slideDown"
                        initial={{ scale: 0.95, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                    >
                        <div className="modal-header">
                            <h2>{selectedBook.title || selectedBook.name}</h2>
                            <div style={{ display: 'flex', gap: '12px' }}>
                                <button className="upload-btn" style={{ padding: '8px 16px', fontSize: '0.9rem' }} onClick={() => handleGenerate(selectedGenerationType, selectedBook.book_id)}>
                                    Consult AI Scholar <FaBookReader style={{ marginLeft: '8px' }} />
                                </button>
                                <button onClick={closeModal} className="close-btn"><FaTimes size={20} /></button>
                            </div>
                        </div>
                        <div className="modal-body" style={{ minHeight: '60vh', display: 'flex' }}>
                            {bookDataUrl ? (
                                bookType === "pdf" ? (
                                    <FlipBook pdfFile={bookDataUrl} closePreview={closeModal} />
                                ) : bookType === "epub" ? (
                                    <FlipBook epubFile={bookDataUrl} closePreview={closeModal} />
                                ) : (
                                    <p style={{ textAlign: 'center', width: '100%', padding: '50px', color: 'var(--lib-text)' }}>Unsupported Format</p>
                                )
                            ) : (
                                <div className="elegant-spinner">
                                    <div className="spinner-circle"></div>
                                    <div>Preparing Manuscript...</div>
                                </div>
                            )}
                        </div>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;