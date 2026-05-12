import OpenAI from "openai";

import {
  extractionPrompt,
  validationPrompt,
  reviewPrompt,
} from "./prompts.js";

const EXTRACT_MODEL = "gpt-4.1-mini";
const VALIDATE_MODEL = "gpt-4.1-mini";
const REVIEW_MODEL = "gpt-4.1";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export function cleanJson(text = "") {
  const cleaned = String(text)
    .trim()
    .replace(/```json/g, "")
    .replace(/```/g, "")
    .trim();

  const start = cleaned.indexOf("{");
  const end = cleaned.lastIndexOf("}");

  if (start === -1 || end === -1) {
    throw new Error(`No se encontró JSON válido: ${cleaned}`);
  }

  return JSON.parse(cleaned.slice(start, end + 1));
}

export async function callVision({ base64, mimeType, prompt, model }) {
  if (!base64 || !mimeType || !prompt || !model) {
    throw new Error("Missing base64, mimeType, prompt or model");
  }

  const response = await client.responses.create({
    model,
    input: [
      {
        role: "user",
        content: [
          {
            type: "input_text",
            text: prompt,
          },
          {
            type: "input_image",
            image_url: `data:${mimeType};base64,${base64}`,
          },
        ],
      },
    ],
  });

  return cleanJson(response.output_text);
}

export function extractData({ base64, mimeType }) {
  return callVision({
    base64,
    mimeType,
    prompt: extractionPrompt(),
    model: EXTRACT_MODEL,
  });
}

export function validateData({ base64, mimeType, extractedData }) {
  return callVision({
    base64,
    mimeType,
    prompt: validationPrompt(extractedData),
    model: VALIDATE_MODEL,
  });
}

export function reviewData({ base64, mimeType, validatedData }) {
  return callVision({
    base64,
    mimeType,
    prompt: reviewPrompt(validatedData),
    model: REVIEW_MODEL,
  });
}
