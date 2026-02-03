import React, { useState } from "react";
import Recorder from "./Recorder.jsx";
import { api } from "./api.js";

function App() {
  const [transcribedText, setTranscribedText] = useState("");
  const [recipientName, setRecipientName] = useState("");
  const [intent, setIntent] = useState("");
  const [emailBody, setEmailBody] = useState("");
  const [subject, setSubject] = useState("");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");

  const handleTranscription = (data) => {
    setTranscribedText(data.transcribed_text || "");
    setRecipientName(data.recipient_name || "");
    setIntent(data.intent || "");
    setStatus("Transcription completed. Review and generate email.");
  };

  const handleGenerateEmail = async () => {
    if (!transcribedText.trim()) {
      setStatus("Please record or paste some text first.");
      return;
    }
    setLoading(true);
    setStatus("Generating professional email with Gemini...");
    try {
      const res = await api.generateEmail({
        transcribed_text: transcribedText,
        recipient_name: recipientName || null,
        intent: intent || null
      });
      setEmailBody(res.email_body || "");
      setSubject(res.subject || "");
      setStatus("Email generated. Review and send.");
    } catch (err) {
      setStatus(err.message || "Failed to generate email.");
    } finally {
      setLoading(false);
    }
  };

  const handleSendEmail = async () => {
    if (!emailBody.trim() || !subject.trim()) {
      setStatus("Generate the email and subject before sending.");
      return;
    }
    setLoading(true);
    setStatus("Sending email securely...");
    try {
      const res = await api.sendEmail({
        transcribed_text: transcribedText,
        recipient_name: recipientName || null,
        intent: intent || null,
        email_body: emailBody,
        subject
      });
      setRecipientEmail(res.recipient_email || "");
      setStatus("Email sent successfully.");
    } catch (err) {
      setStatus(err.message || "Failed to send email.");
    } finally {
      setLoading(false);
    }
  };

  const refreshContacts = async () => {
    try {
      const list = await api.listContacts();
      setContacts(list);
    } catch (err) {
      setStatus(err.message || "Failed to load contacts.");
    }
  };

  const handleAddContact = async (event) => {
    event.preventDefault();
    const form = event.target;
    const name = form.name.value.trim();
    const email = form.email.value.trim();
    if (!name || !email) return;
    try {
      await api.addContact({ name, email });
      form.reset();
      await refreshContacts();
      setStatus("Contact saved.");
    } catch (err) {
      setStatus(err.message || "Failed to save contact.");
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>MailCrafter</h1>
        <p>Speech-to-Email Assistant powered by Gemini</p>
      </header>

      <main className="layout" aria-label="Speech to email workflow">
        <section className="panel" aria-label="Record or paste message">
          <h2>1. Capture your message</h2>
          <Recorder onTranscribed={handleTranscription} />

          <label htmlFor="transcribed-text" className="field-label">
            Transcribed text
          </label>
          <textarea
            id="transcribed-text"
            value={transcribedText}
            onChange={(e) => setTranscribedText(e.target.value)}
            rows={6}
          />

          <div className="field-row">
            <div className="field">
              <label htmlFor="recipient-name">Recipient name</label>
              <input
                id="recipient-name"
                type="text"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="intent">Intent (optional)</label>
              <input
                id="intent"
                type="text"
                value={intent}
                onChange={(e) => setIntent(e.target.value)}
                placeholder="e.g. follow_up, meeting_request"
              />
            </div>
          </div>

          <button
            type="button"
            className="primary"
            onClick={handleGenerateEmail}
            disabled={loading}
          >
            Generate professional email
          </button>
        </section>

        <section className="panel" aria-label="Review and send email">
          <h2>2. Review & send</h2>

          <label htmlFor="subject" className="field-label">
            Subject
          </label>
          <input
            id="subject"
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />

          <label htmlFor="email-body" className="field-label">
            Email body
          </label>
          <textarea
            id="email-body"
            value={emailBody}
            onChange={(e) => setEmailBody(e.target.value)}
            rows={10}
          />

          <button
            type="button"
            className="primary"
            onClick={handleSendEmail}
            disabled={loading}
          >
            Send email
          </button>

          {recipientEmail && (
            <p className="hint">
              Sent to: <strong>{recipientEmail}</strong>
            </p>
          )}
        </section>

        <section className="panel" aria-label="Contacts">
          <h2>3. Contacts</h2>
          <button type="button" onClick={refreshContacts}>
            Refresh contacts
          </button>

          <ul className="contacts-list">
            {contacts.map((c) => (
              <li key={c.id}>
                <span className="contact-name">{c.name}</span>
                <span className="contact-email">{c.email}</span>
              </li>
            ))}
            {contacts.length === 0 && (
              <li className="hint">No contacts yet. Add one below.</li>
            )}
          </ul>

          <form onSubmit={handleAddContact} className="contacts-form">
            <div className="field-row">
              <div className="field">
                <label htmlFor="contact-name">Name</label>
                <input id="contact-name" name="name" type="text" required />
              </div>
              <div className="field">
                <label htmlFor="contact-email">Email</label>
                <input id="contact-email" name="email" type="email" required />
              </div>
            </div>
            <button type="submit">Add / Update contact</button>
          </form>
        </section>
      </main>

      <footer className="status-bar" aria-live="polite">
        {loading ? "Working..." : status}
      </footer>
    </div>
  );
}

export default App;

