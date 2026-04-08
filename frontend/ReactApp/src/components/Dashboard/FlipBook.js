import React, { useState } from "react";
import HTMLFlipBook from "react-pageflip";
import { Document, Page, pdfjs } from "react-pdf";
// import ePub from "epubjs";
// import "./FlipBook.css";
import { ReactReader } from "react-reader";


pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

const FlipBook = ({ pdfFile, epubFile, closePreview }) => {
    const [numPages, setNumPages] = useState(0);

    return (
        <div className="flipbook-container">
            <button className="close-btn" onClick={closePreview}>X</button>

            {pdfFile ? (
                <div className="flipbook-wrapper">
                    <Document file={pdfFile} onLoadSuccess={({ numPages }) => setNumPages(numPages)}>
                        <HTMLFlipBook
                            width={400}
                            height={600}
                            size="stretch"
                            minWidth={400}
                            maxWidth={800}
                            minHeight={600}
                            maxHeight={1200}
                            showCover={true}
                            drawShadow={true}
                            flippingTime={1200} // More natural flip animation
                            maxShadowOpacity={0.5}
                            usePortrait={false}  // Enable double-page view
                            startPage={0} // Start from the first page
                            autoSize={true} // Ensures content scales properly
                            clickEventForward={false}
                            swipeDistance={0}
                            className="animated-book"
                        >
                            {Array.from({ length: numPages }, (_, index) => (
                                <div key={index} className="page">
                                    <Page pageNumber={index + 1} width={400} />
                                </div>
                            ))}
                        </HTMLFlipBook>
                    </Document>
                </div>
            ) : epubFile ? (
                <div className="flipbook-wrapper">

                    <ReactReader
                        url={epubFile}
                        epubInitOptions={{
                            openAs: "epub"
                        }}
                        epubOptions={{
                            flow: "paginated",
                            manager: "continuous",
                            width: "100%"
                        }}
                    />
                </div>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
};

export default FlipBook;
