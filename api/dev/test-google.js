import { google } from "googleapis";

import { extractData, validateData } from "../../lib/guia/ai.js";
import { normalizeResult } from "../../lib/guia/schema.js";

export default async function handler(req, res) {
  try {
    const clientEmail = process.env.GOOGLE_CLIENT_EMAIL;
    const privateKey = process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, "\n");
    const folderId = process.env.GOOGLE_DRIVE_FOLDER_ID;

    if (!clientEmail || !privateKey || !folderId) {
      return res.status(500).json({
        ok: false,
        error: "Missing GOOGLE_CLIENT_EMAIL, GOOGLE_PRIVATE_KEY or GOOGLE_DRIVE_FOLDER_ID",
      });
    }

    if (!process.env.OPENAI_API_KEY) {
      return res.status(500).json({
        ok: false,
        error: "Missing OPENAI_API_KEY",
      });
    }

    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: clientEmail,
        private_key: privateKey,
      },
      scopes: ["https://www.googleapis.com/auth/drive.readonly"],
    });

    const client = await auth.getClient();
    const drive = google.drive({ version: "v3", auth: client });

    const listResponse = await drive.files.list({
      q: `'${folderId}' in parents and trashed = false`,
      fields: "files(id,name,mimeType,createdTime,modifiedTime)",
      orderBy: "createdTime desc",
      pageSize: 50,
      supportsAllDrives: true,
      includeItemsFromAllDrives: true,
    });

    const files = listResponse.data.files || [];
    const firstImage = files.find((file) => file.mimeType?.startsWith("image/"));

    if (!firstImage) {
      return res.status(200).json({
        ok: true,
        folderId,
        count: files.length,
        files,
        result: null,
      });
    }

    const downloadResponse = await drive.files.get(
      {
        fileId: firstImage.id,
        alt: "media",
        supportsAllDrives: true,
      },
      { responseType: "arraybuffer" }
    );

    const buffer = Buffer.from(downloadResponse.data);
    const base64 = buffer.toString("base64");

    const extracted = await extractData({
      base64,
      mimeType: firstImage.mimeType,
    });

    const validation = await validateData({
      base64,
      mimeType: firstImage.mimeType,
      extractedData: extracted,
    });

    const result = normalizeResult({
      ...extracted,
      ...validation,
    });

    return res.status(200).json({
      ok: true,
      folderId,
      count: files.length,
      file: {
        id: firstImage.id,
        name: firstImage.name,
        mimeType: firstImage.mimeType,
        sizeBytes: buffer.length,
      },
      extracted,
      validation,
      result,
    });
  } catch (error) {
    console.error("test-google process error", error);

    return res.status(500).json({
      ok: false,
      error: error.message,
    });
  }
}
