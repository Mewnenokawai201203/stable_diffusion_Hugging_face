
async function generateImage() {
    const prompt = document.getElementById("prompt").value;

    if (!prompt.trim()) {
        alert("Vui lòng nhập lại!");
        return;
    }

    document.getElementById("result").innerHTML = `<p>Loading...</p>`;

    const maxRetries = 5; 
    const retryDelay = 5000; 

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const response = await fetch("/generate-image", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.status === "success") {
                
                const timestamp = new Date().getTime();
                const imageUrl = `${data.image_url}?t=${timestamp}`;
                document.getElementById("result").innerHTML = `
                    <img src="${imageUrl}" alt="Generated Image" style="max-width: 500px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);">
                `;
                document.getElementById("result").innerHTML = `
                <img src="${data.image_url}" alt="Generated Image" style="max-width: 500px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);">
                <br>
                <a href="${data.download_url}" download style="text-decoration: none;">
                    <button style="margin-top: 10px; padding: 10px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        Tải Ảnh Về
                    </button>
                </a>
                `;
                return; 
            } else if (data.error && data.error.includes("currently loading")) {
                if (attempt < maxRetries) {
                    console.log(`Model is loading. Retrying in ${retryDelay / 1000} seconds...`);
                    document.getElementById("result").innerHTML = `<p>Model is loading. Retrying (${attempt}/${maxRetries})...</p>`;
                    await new Promise(resolve => setTimeout(resolve, retryDelay)); 
                } else {
                    throw new Error("Model failed to load after multiple attempts.");
                }
            } else {
                alert("Error: " + data.message);
                break; 
            }
        } catch (error) {
            console.error("Error:", error);
            if (attempt === maxRetries) {
                document.getElementById("result").innerHTML = `<p>An error occurred while generating the image. Please try again later.</p>`;
            } else {
                document.getElementById("result").innerHTML = `<p>Retrying... (${attempt}/${maxRetries})</p>`;
                await new Promise(resolve => setTimeout(resolve, retryDelay)); 
            }
        }
    }
}

