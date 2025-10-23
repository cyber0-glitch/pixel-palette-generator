const LARGE_IMAGE_THRESHOLD = 50_000_000;

const form = document.getElementById("generator-form");
const modeSelect = document.getElementById("mode-select");
const paletteFieldset = document.getElementById("palette-fieldset");
const colorsField = document.getElementById("colors-field");
const colorsInput = document.getElementById("colors-input");
const seedInput = document.getElementById("seed-input");
const sizeInput = document.getElementById("size-input");
const generateBtn = document.getElementById("generate-btn");
const cancelBtn = document.getElementById("cancel-btn");
const downloadBtn = document.getElementById("download-btn");
const canvas = document.getElementById("preview-canvas");
const progressText = document.getElementById("progress-text");
const messages = document.getElementById("messages");

let currentTask = null;

function setMessage(text, kind = "info") {
  messages.textContent = text;
  if (kind === "error") {
    messages.classList.add("error");
  } else {
    messages.classList.remove("error");
  }
}

function parseSize(value) {
  const parts = value.toLowerCase().split("x");
  if (parts.length !== 2) {
    throw new Error("Size must use WIDTHxHEIGHT format.");
  }
  const width = parseInt(parts[0], 10);
  const height = parseInt(parts[1], 10);
  if (!Number.isFinite(width) || !Number.isFinite(height) || width <= 0 || height <= 0) {
    throw new Error("Width and height must be positive integers.");
  }
  return { width, height };
}

function parseHexColor(value) {
  const trimmed = value.trim();
  const match = trimmed.match(/^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/);
  if (!match) {
    throw new Error(`Invalid color: ${value}`);
  }
  let hex = match[1];
  if (hex.length === 3) {
    hex = hex
      .split("")
      .map((ch) => ch + ch)
      .join("");
  }
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  return [r, g, b];
}

function parseColors(value) {
  if (!value) {
    return [];
  }
  const colors = value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean)
    .map(parseHexColor);
  if (!colors.length) {
    throw new Error("Provide at least one valid hex color.");
  }
  return colors;
}

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function createRng(seed) {
  if (seed === null || seed === undefined || seed === "") {
    return Math.random;
  }
  const num = Number(seed);
  if (!Number.isFinite(num)) {
    throw new Error("Seed must be an integer.");
  }
  return mulberry32(num);
}

function getSelectedPaletteName() {
  const radios = paletteFieldset.querySelectorAll('input[name="palette"]');
  for (const radio of radios) {
    if (radio.checked) {
      return radio.value;
    }
  }
  return "bw";
}

function buildPalette(mode, paletteName, colors) {
  if (colors.length) {
    return { type: "list", name: "custom", colors };
  }
  if (mode === "custom") {
    throw new Error("Custom mode requires at least one color.");
  }
  switch (paletteName) {
    case "bw":
      return { type: "list", name: "bw", colors: [
        [0, 0, 0],
        [255, 255, 255],
      ] };
    case "grayscale": {
      const shades = Array.from({ length: 256 }, (_, i) => [i, i, i]);
      return { type: "list", name: "grayscale", colors: shades };
    }
    case "all":
      return { type: "all", name: "all" };
    default:
      throw new Error(`Unknown palette: ${paletteName}`);
  }
}

function createColorPicker(palette, rng) {
  if (palette.type === "list") {
    const colors = palette.colors;
    if (!colors || !colors.length) {
      throw new Error("Palette has no colors.");
    }
    return () => {
      const raw = rng() * colors.length;
      const index = Math.min(colors.length - 1, Math.floor(raw));
      return colors[index];
    };
  }
  if (palette.type === "all") {
    return () => [
      Math.floor(rng() * 256),
      Math.floor(rng() * 256),
      Math.floor(rng() * 256),
    ];
  }
  throw new Error("Unsupported palette type");
}

function toggleModeFields() {
  const mode = modeSelect.value;
  if (mode === "custom") {
    paletteFieldset.hidden = true;
    colorsField.hidden = false;
  } else {
    paletteFieldset.hidden = false;
    colorsField.hidden = true;
  }
}

modeSelect.addEventListener("change", toggleModeFields);
toggleModeFields();

function setGeneratingState(isGenerating) {
  generateBtn.disabled = isGenerating;
  cancelBtn.disabled = !isGenerating;
  downloadBtn.disabled = true;
  if (!isGenerating) {
    currentTask = null;
  }
}

cancelBtn.addEventListener("click", () => {
  if (currentTask) {
    currentTask.cancelled = true;
    setMessage("Generation cancelled.");
  }
});

downloadBtn.addEventListener("click", () => {
  canvas.toBlob((blob) => {
    if (!blob) {
      setMessage("Unable to export image.", "error");
      return;
    }
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "pixel-palette.png";
    document.body.append(link);
    link.click();
    requestAnimationFrame(() => {
      URL.revokeObjectURL(url);
      link.remove();
    });
  }, "image/png");
});

function updateProgress(row, total, elapsedSeconds) {
  const percent = ((row / total) * 100).toFixed(1);
  progressText.textContent = `Row ${row} / ${total} (${percent}% • ${elapsedSeconds.toFixed(1)}s)`;
}

function resetProgress() {
  progressText.textContent = "No image yet.";
}

function generateImage({ width, height, palette, rng }) {
  const ctx = canvas.getContext("2d");
  canvas.width = width;
  canvas.height = height;
  ctx.clearRect(0, 0, width, height);

  const pickColor = createColorPicker(palette, rng);
  const rowData = ctx.createImageData(width, 1);
  const startTime = performance.now();
  let row = 0;

  currentTask = { cancelled: false };

  function step() {
    if (!currentTask || currentTask.cancelled) {
      setGeneratingState(false);
      resetProgress();
      return;
    }

    const chunkSize = Math.min(64, height - row);
    for (let chunkRow = 0; chunkRow < chunkSize; chunkRow += 1) {
      if (currentTask.cancelled) {
        setGeneratingState(false);
        resetProgress();
        return;
      }
      const data = rowData.data;
      for (let x = 0; x < width; x += 1) {
        const [r, g, b] = pickColor();
        const offset = x * 4;
        data[offset] = r;
        data[offset + 1] = g;
        data[offset + 2] = b;
        data[offset + 3] = 255;
      }
      ctx.putImageData(rowData, 0, row);
      row += 1;
      updateProgress(row, height, (performance.now() - startTime) / 1000);
    }

    if (row < height) {
      requestAnimationFrame(step);
    } else {
      setGeneratingState(false);
      setMessage("Image ready! Download whenever you're happy with it.");
      downloadBtn.disabled = false;
    }
  }

  requestAnimationFrame(step);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();

  try {
    const { width, height } = parseSize(sizeInput.value.trim());
    const mode = modeSelect.value;
    const paletteName = getSelectedPaletteName();
    const customColors = parseColors(colorsInput.value);
    const rng = createRng(seedInput.value);
    const palette = buildPalette(mode, paletteName, customColors);

    const totalPixels = width * height;
    if (totalPixels > LARGE_IMAGE_THRESHOLD) {
      const proceed = window.confirm(
        `The requested image has ${totalPixels.toLocaleString()} pixels and may be slow to render. Continue?`
      );
      if (!proceed) {
        setMessage("Generation cancelled by user.");
        return;
      }
    }

    const statusMessage =
      mode !== "custom" && customColors.length
        ? "Custom colors override the selected palette. Generating image…"
        : "Generating image…";
    setMessage(statusMessage);
    setGeneratingState(true);
    updateProgress(0, height || 1, 0);
    generateImage({ width, height, palette, rng });
  } catch (error) {
    setMessage(error.message || String(error), "error");
  }
});
