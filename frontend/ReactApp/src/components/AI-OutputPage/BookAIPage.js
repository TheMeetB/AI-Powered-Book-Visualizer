
import React, { useEffect, useState, useRef } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import JSZip from "jszip";
import { useCallback } from "react";
import { FaSearch, FaUserCircle, FaSun, FaMoon, FaSignOutAlt, FaBell } from "react-icons/fa";
import { FiBookOpen } from "react-icons/fi";
import "./BookAIPage.css";
import api from "../../api";
// import dashboard from "../Dashboard/Dashboard";

const BookSummaryGenerator = () => {
    const storedUserid = sessionStorage.getItem("userId");
    const storedToken = sessionStorage.getItem("accessToken");
    const storedUsername = sessionStorage.getItem("username");
    const location = useLocation();
    const navigate = useNavigate();
    const bookId = location.state?.bookId;
    const [imageFiles, setImageFiles] = useState([]);
    const [selectedImageIndex, setSelectedImageIndex] = useState(null);
    const [loadingImages, setLoadingImages] = useState(false);
    // State management
    const [summary, setSummary] = useState([]);
    const [displayedSummary, setDisplayedSummary] = useState("");
    const [fullSummary, setFullSummary] = useState("");
    const [selectedAudioIndex, setSelectedAudioIndex] = useState(null);
    const [typingIndex, setTypingIndex] = useState(0);
    const [loadingSummary, setLoadingSummary] = useState(true);
    const [darkMode, setDarkMode] = useState(false);
    const [audioFiles, setAudioFiles] = useState([]);
    const [showNotification, setShowNotification] = useState(false);

    const [showAudioBox, setShowAudioBox] = useState(false);
    const [books, setBooks] = useState(null);
    const [isProfileOpen, setIsProfileOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [filteredBooks, setFilteredBooks] = useState([]);
    const audioRef = useRef(null);
    const typingSpeed = 3; // Adjust speed (milliseconds per letter)

    const toggleProfileMenu = () => setIsProfileOpen(!isProfileOpen);
    const toggleTheme = () => setDarkMode(!darkMode);
    const logout = () => {
        sessionStorage.removeItem("accessToken");
        navigate("/");
    };
    const fetchSummary = useCallback(async (bookId) => {
        setLoadingSummary(true);
        setFullSummary("");
        setDisplayedSummary("");
        setTypingIndex(0);

        try {
            const response = await api.get(`book/${bookId}/summary`, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${storedToken}`
                }
            });

            console.log("[response]:", response);

            // Ensure `summary` is an array of objects (chapter-wise)
            const chapterSummaries = response.data.data.map(ch => ({
                chapter_id: ch.chapter_id,
                summary: ch.summary
            }));

            setSummary(chapterSummaries); // ✅ This ensures `BookFlip` gets the correct data

            // Convert summary to HTML format for the progressive text display
            const formattedSummary = chapterSummaries
                .map(ch => `<strong>Chapter ${ch.chapter_id}:</strong> ${ch.summary}`)
                .join("<br><br>");
            sessionStorage.setItem(`summary_${bookId}`, formattedSummary);
            setFullSummary(formattedSummary.trim() ? formattedSummary : "No summary available.");
        } catch (error) {
            console.error("Error fetching summary:", error);
            setFullSummary("Error loading summary.");
        } finally {
            setLoadingSummary(false);
        }
    }, [storedToken]);

    useEffect(() => {
        if (bookId && !fullSummary) {
            fetchSummary(bookId);
        }
    }, [bookId, fullSummary, fetchSummary]);

    useEffect(() => {
        console.log("ShowAudioBox updated:", showAudioBox);
    }, [showAudioBox]);


    useEffect(() => {
        const savedTypingIndex = sessionStorage.getItem(`typingIndex_${bookId}`);
        const savedDisplayedSummary = sessionStorage.getItem(`displayedSummary_${bookId}`);

        if (savedTypingIndex && savedDisplayedSummary) {
            setTypingIndex(parseInt(savedTypingIndex, 10));
            setDisplayedSummary(savedDisplayedSummary);
        }
    }, [bookId]);

    useEffect(() => {
        if (fullSummary.length > 0 && typingIndex < fullSummary.length) {
            const timeout = setTimeout(() => {
                setDisplayedSummary(prev => {
                    const updatedSummary = prev + fullSummary[typingIndex];

                    // Save progress in session storage
                    sessionStorage.setItem(`typingIndex_${bookId}`, typingIndex + 1);
                    sessionStorage.setItem(`displayedSummary_${bookId}`, updatedSummary);

                    return updatedSummary;
                });
                setTypingIndex(prev => prev + 1);
            }, typingSpeed);

            return () => clearTimeout(timeout);
        }
    }, [typingIndex, fullSummary]);

    // Restart Typing on Summary Change
    useEffect(() => {
        if (fullSummary &&
            typingIndex === fullSummary.length &&
            fullSummary !== "No summary available." &&
            fullSummary !== "Error loading summary."
        ) {
            setShowNotification(true);
            const timer = setTimeout(() => setShowNotification(false), 3000);
            return () => clearTimeout(timer);
        }
    }, [typingIndex, fullSummary]);

    // Fetch Books
    useEffect(() => {
        const fetchBooks = async () => {
            try {
                const response = await api.get(`dashboard/get_all_books/${storedUserid}`, {
                    headers: { "Content-Type": "application/json", Authorization: `Bearer ${storedToken}` }
                });
                setBooks(response.data.data || []);
            } catch (error) {
                console.error("Error getting books:", error);
            }
        };

        if (storedUserid && storedToken) fetchBooks();
    }, [storedUserid, storedToken]);

    // Search books
    useEffect(() => {
        if (searchQuery) {
            setFilteredBooks(books?.filter(book => book.title.toLowerCase().includes(searchQuery.toLowerCase())) || []);
        } else {
            setFilteredBooks([]);
        }
    }, [searchQuery, books]);
    const fetchAudio = async (bookId) => {
        try {
            // setLoadingAudio(true);
            // setError(null);

            const response = await api.get(`book/${bookId}/audio`, {
                responseType: "blob",
                headers: { "Authorization": `Bearer ${storedToken}` }
            });

            const zip = new JSZip();
            const zipContents = await zip.loadAsync(response.data);

            const audioList = [];
            for (const filename in zipContents.files) {
                if (filename.endsWith(".mp3") || filename.endsWith(".wav")) {
                    const fileData = await zipContents.files[filename].async("blob");
                    const audioUrl = URL.createObjectURL(fileData);
                    audioList.push({ name: filename, url: audioUrl });
                }
            }

            setAudioFiles(audioList);
            setShowAudioBox(true); // Show dropdown after fetching audio
        } catch (error) {
            console.error("Error fetching audio:", error);
            // setError("Failed to load audio.");
        } finally {
            // setLoadingAudio(false);
        }
    };
    const handleAudioSelection = (index) => {
        const selectedIndex = parseInt(index, 10); // Convert index to number
        setSelectedAudioIndex(selectedIndex);
        // setCurrentIndex(selectedIndex); // Ensure currentIndex is updated for playback

        setTimeout(() => {
            if (audioRef.current) {
                audioRef.current.load();  // Reload audio to apply new source
                audioRef.current.play();  // Play the selected chapter
            }
        }, 100);
    };
    const fetchImages = async (bookId) => {
        try {
            setLoadingImages(true);
            const response = await api.get(`book/${bookId}/image`, {
                responseType: "blob",
                headers: { "Authorization": `Bearer ${storedToken}` }
            });

            const zip = new JSZip();
            const zipContents = await zip.loadAsync(response.data);
            const imageList = [];

            for (const filename in zipContents.files) {
                if (filename.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
                    const fileData = await zipContents.files[filename].async("blob");
                    const imageUrl = URL.createObjectURL(fileData);
                    imageList.push({ name: filename, url: imageUrl });
                }
            }

            setImageFiles(imageList);
        } catch (error) {
            console.error("Error fetching images:", error);
            // setError("Failed to load images.");
        } finally {
            setLoadingImages(false);
        }
    };
    return (
        <div className={`book-summary-app ${darkMode ? "dark-mode" : "light-mode"}`}>
            {true && (
                <header className="dashboard-header">
                    <div className="logo-div">
                        <Link to="/dashboard">
                            <FiBookOpen size={24} /> <span>Book Visualizer</span>
                        </Link>
                    </div>
                    <div className="search-bar">
                        <input type="text" placeholder="Search books..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
                        <FaSearch className="search-icon" />
                    </div>
                    <div className="header-icons">
                        <div className="profile-container">
                            <FaUserCircle className="profile-icon" onClick={toggleProfileMenu} />
                            {isProfileOpen && (
                                <div className="profile-menu">
                                    <p>Welcome, <strong>{storedUsername}</strong>!</p>
                                    <button className="profile-option" onClick={toggleTheme}>
                                        {darkMode ? <><FaSun /> Light Mode</> : <><FaMoon /> Dark Mode</>}
                                    </button>
                                    <button className="profile-option" onClick={logout}><FaSignOutAlt /> Logout</button>
                                </div>
                            )}
                        </div>
                        {showNotification && (
                            <div className={`notification ${darkMode ? 'dark' : 'light'}`}>
                                <FaBell className="notification-bell" />
                                <span>Summary generated successfully!</span>
                            </div>
                        )}
                    </div>
                </header>
            )}
            <div className="content-wrapper">
                <div className={`container left-box fullscreen`}>
                    {loadingSummary ? (
                        <p className="loading-text">Loading summary...</p>
                    ) : fullSummary.length > 0 && fullSummary !== "No summary available." ? (
                        <div className="summary-content interactive-box">
                            <h2 className="chapter-summary-header">
                                📚 Chapter Summaries
                                <span className="audiobook-icon"
                                    onClick={() => fetchAudio(bookId)}
                                    role="button"
                                    tabIndex={0}
                                    aria-label="Generate Audio"
                                    onKeyPress={(e) => { if (e.key === "Enter") fetchAudio(bookId); }}
                                >
                                    🔊
                                </span>

                                {showAudioBox && audioFiles.length > 0 && (
                                    <select
                                        className="audio-dropdown"
                                        onChange={(e) => handleAudioSelection(e.target.value)}
                                        defaultValue=""
                                    >
                                        <option value="" disabled>Select a chapter</option>
                                        {audioFiles.map((audio, index) => (
                                            <option key={index} value={index}>{`Chapter ${index + 1}`}</option>
                                        ))}
                                    </select>
                                )}

                                <span className="image-icon"
                                    onClick={() => fetchImages(bookId)}
                                    data-tooltip="Generate Image"

                                >🖼️</span>

                                {imageFiles.length > 0 && (
                                    <select
                                        className="image-dropdown"
                                        onChange={(e) => setSelectedImageIndex(e.target.value)}
                                        defaultValue=""
                                    >
                                        <option value="" disabled>Select an image</option>
                                        {imageFiles.map((image, index) => (
                                            <option key={index} value={index}>{`Chapter ${index + 1} Image`}</option>
                                        ))}
                                    </select>
                                )}
                            </h2>

                            {loadingSummary ? (
                                <p className="loading-text">Loading summary...</p>
                            ) : fullSummary === "No summary available." || fullSummary === "Error loading summary." ? (
                                <p className="no-summary">{fullSummary}</p>
                            ) : (
                                <p dangerouslySetInnerHTML={{ __html: displayedSummary }} alt="Summary Content" />
                            )}
                        </div>
                    ) :
                        (
                            <p className="no-summary">No summary available.</p>
                        )}
                </div>
            </div>
            <div className="button-container">
                {selectedAudioIndex !== null && (
                    <div className="audio-player">
                        <audio ref={audioRef} controls autoPlay>
                            <source src={audioFiles[selectedAudioIndex]?.url} type="audio/mpeg" />
                            Your browser does not support the audio element.
                        </audio>

                    </div>
                )}

                <div className="image-container">
                    {selectedImageIndex !== null && (
                        <div className="image-preview">
                            {loadingImages ? (
                                <p className="loading-text">Loading image...</p>
                            ) : (
                                <img
                                    src={imageFiles[selectedImageIndex]?.url}
                                    alt={`Chapter ${selectedImageIndex + 1} Visual`}
                                    className="chapter-image"
                                />
                            )}
                        </div>
                    )}
                </div>

            </div>


        </div>
    );
};

export default BookSummaryGenerator;

