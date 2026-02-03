export const api = {
  async generateEmail(payload) {
    const res = await fetch("/api/v1/email/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || "Failed to generate email");
    }
    return res.json();
  },

  async sendEmail(payload) {
    const res = await fetch("/api/v1/email/send", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || "Failed to send email");
    }
    return res.json();
  },

  async listContacts() {
    const res = await fetch("/api/v1/contacts");
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || "Failed to load contacts");
    }
    return res.json();
  },

  async addContact(contact) {
    const res = await fetch("/api/v1/contacts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(contact)
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || "Failed to save contact");
    }
    return res.json();
  }
};

