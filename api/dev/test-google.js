import { google } from "googleapis";

export default async function handler(req, res) {
  try {
    const clientEmail = process.env.GOOGLE_CLIENT_EMAIL;
    const privateKey = process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, "\n");
    const spreadsheetId = process.env.GOOGLE_SHEET_ID;

    if (!clientEmail || !privateKey || !spreadsheetId) {
      return res.status(500).json({
        ok: false,
        error: "Missing GOOGLE_CLIENT_EMAIL, GOOGLE_PRIVATE_KEY or GOOGLE_SHEET_ID",
      });
    }

    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: clientEmail,
        private_key: privateKey,
      },
      scopes: ["https://www.googleapis.com/auth/spreadsheets"],
    });

    const client = await auth.getClient();
    const sheets = google.sheets({ version: "v4", auth: client });

    await sheets.spreadsheets.values.append({
      spreadsheetId,
      range: "A1",
      valueInputOption: "RAW",
      requestBody: {
        values: [[new Date().toISOString(), "TEST_OK"]],
      },
    });

    return res.status(200).json({ ok: true });
  } catch (error) {
    console.error("test-google error", error);

    return res.status(500).json({
      ok: false,
      error: error.message,
    });
  }
}
