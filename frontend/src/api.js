console.log("API URL:", import.meta.env.VITE_API_URL);
const API_BASE = import.meta.env.VITE_API_URL || "https://mailcrafter-production.up.railway.app/api/v1";

export const api = {
  async generateEmail(payload) {
    const res = await fetch(`${API_BASE}/email/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || "Failed to generate email");
    }

    return res.json();
  },

  async deleteContact(email) {
  const res = await fetch(
    `${API_BASE}/contacts/${encodeURIComponent(email)}`,
    {
      method: "DELETE"
    }
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Failed to delete contact");
  }

  return true;
},

  async sendEmail(payload) {
    const res = await fetch(`${API_BASE}/email/send`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || "Failed to send email");
    }

    return res.json();
  },

  async listContacts() {
    const res = await fetch(`${API_BASE}/contacts`);

    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || "Failed to load contacts");
    }

    return res.json();
  },

  async addContact(contact) {
    const res = await fetch(`${API_BASE}/contacts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(contact)
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || "Failed to save contact");
    }

    return res.json();
  }
};