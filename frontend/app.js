const API_CANDIDATES = [
  "http://localhost:8010",
  "http://127.0.0.1:8010",
  "http://localhost:8000",
  "http://127.0.0.1:8000",
  "http://localhost:8001",
  "http://127.0.0.1:8001",
];
let API_BASE = API_CANDIDATES[0];

const form = document.querySelector("#knock-form");
const submitButton = document.querySelector("#submit-button");
const statusLine = document.querySelector("#status-line");
const resultSection = document.querySelector("#result-section");
const imageBlock = document.querySelector("#image-block");
const generatedImage = document.querySelector("#generated-image");

const fields = {
  leave_behind: document.querySelector("#leave-behind"),
  threshold: document.querySelector("#threshold"),
  hope_to_hear: document.querySelector("#hope-to-hear"),
};

const resultFields = {
  emotionTitle: document.querySelector("#emotion-title"),
  emotionDescription: document.querySelector("#emotion-description"),
  motifList: document.querySelector("#motif-list"),
  lensList: document.querySelector("#lens-list"),
  manifestoText: document.querySelector("#manifesto-text"),
  imagePrompt: document.querySelector("#image-prompt"),
  historicalInfluence: document.querySelector("#historical-influence"),
};

checkHealth();

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    leave_behind: fields.leave_behind.value.trim(),
    threshold: fields.threshold.value.trim(),
    hope_to_hear: fields.hope_to_hear.value.trim(),
  };

  if (!payload.leave_behind || !payload.threshold || !payload.hope_to_hear) {
    setStatus("All three answers are needed before the door can be designed.", true);
    return;
  }

  setLoading(true);
  setStatus("Listening for the knock...");

  try {
    const response = await fetch(`${API_BASE}/api/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await parseJson(response);

    if (!response.ok && hasRenderableArtwork(data)) {
      renderResult(data);
      setStatus("The backend recovered with a fallback artwork.", true);
      return;
    }

    if (!response.ok) {
      throw new Error(data.detail || "The backend could not complete the generation.");
    }

    renderResult(data);
    setStatus(data.image_url_or_path ? "The door opened with an image." : "The door opened with text and prompt.");
  } catch (error) {
    setStatus(`Generation failed: ${error.message}`, true);
  } finally {
    setLoading(false);
  }
});

async function checkHealth() {
  for (const candidate of API_CANDIDATES) {
    try {
      const response = await fetch(`${candidate}/api/health`);
      if (!response.ok) {
        continue;
      }

      const data = await response.json();
      API_BASE = candidate;
      const aiStatus = providerStatus(data.text_provider, data.ai_configured);
      setStatus(`Backend connected on ${candidate}. ${aiStatus}`);
      return;
    } catch {
      // Try the next known local backend address.
    }
  }

  setStatus("Start the FastAPI backend before designing a door.", true);
}

function renderResult(data) {
  resultFields.emotionTitle.textContent = `${data.emotion.dominant_emotion} (${Math.round(
    data.emotion.score * 100,
  )}%)`;
  resultFields.emotionDescription.textContent = data.emotion.description;
  renderMotifs(data.motifs || []);
  renderContextLenses(data.context_lenses || []);
  resultFields.manifestoText.textContent = data.manifesto_text;
  resultFields.imagePrompt.textContent = data.image_prompt;
  resultFields.historicalInfluence.textContent = data.historical_influence;

  if (data.image_url_or_path) {
    generatedImage.src = resolveImageUrl(data.image_url_or_path);
    imageBlock.classList.remove("hidden");
  } else {
    generatedImage.removeAttribute("src");
    imageBlock.classList.add("hidden");
  }

  resultSection.classList.remove("hidden");
  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function resolveImageUrl(path) {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }

  if (path.startsWith("/")) {
    return `${API_BASE}${path}`;
  }

  return `${API_BASE}/${path}`;
}

function setLoading(isLoading) {
  submitButton.disabled = isLoading;
  submitButton.classList.toggle("loading", isLoading);
}

function setStatus(message, isError = false) {
  statusLine.textContent = message;
  statusLine.classList.toggle("error", isError);
}

function renderMotifs(motifs) {
  resultFields.motifList.innerHTML = "";

  if (!motifs.length) {
    const emptyItem = document.createElement("li");
    emptyItem.textContent = "The door stayed quiet; no motifs were detected.";
    resultFields.motifList.appendChild(emptyItem);
    return;
  }

  motifs.forEach((motif) => {
    const item = document.createElement("li");
    const name = document.createElement("span");
    const symbol = document.createElement("span");
    const meaning = document.createElement("span");

    name.className = "motif-name";
    symbol.className = "motif-symbol";
    meaning.className = "motif-meaning";

    name.textContent = `${motif.name} (${Math.round(motif.score * 10) / 10})`;
    symbol.textContent = motif.symbol;
    meaning.textContent = motif.meaning;

    item.append(name, symbol, meaning);
    resultFields.motifList.appendChild(item);
  });
}

function renderContextLenses(lenses) {
  resultFields.lensList.innerHTML = "";

  if (!lenses.length) {
    const emptyItem = document.createElement("li");
    emptyItem.textContent = "No historical lenses were selected.";
    resultFields.lensList.appendChild(emptyItem);
    return;
  }

  lenses.forEach((lens) => {
    const item = document.createElement("li");
    const name = document.createElement("span");
    const summary = document.createElement("span");
    const meta = document.createElement("span");

    name.className = "lens-name";
    summary.className = "lens-summary";
    meta.className = "lens-meta";

    const terms = lens.matched_terms && lens.matched_terms.length ? lens.matched_terms.join(", ") : "emotion prior";
    name.textContent = lens.title;
    summary.textContent = lens.summary;
    meta.textContent = `${lens.source} / relevance ${lens.relevance} / ${terms}`;

    item.append(name, summary, meta);
    resultFields.lensList.appendChild(item);
  });
}

async function parseJson(response) {
  try {
    return await response.json();
  } catch {
    return {};
  }
}

function hasRenderableArtwork(data) {
  return data && data.emotion && data.manifesto_text && data.image_prompt && data.historical_influence;
}

function providerStatus(provider, configured) {
  if (provider === "gemini") {
    return "Gemini text generation is configured.";
  }

  if (provider === "openai") {
    return "OpenAI text generation is configured.";
  }

  return configured ? "Cloud AI is configured." : "Local fallback mode is ready.";
}
