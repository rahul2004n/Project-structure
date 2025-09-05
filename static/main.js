// static/main.js

document.addEventListener("DOMContentLoaded", () => {
  console.log("Autonomous AP Prototype loaded ✅");

  // Auto-refresh invoices every 30 seconds
  setInterval(fetchInvoices, 30000);

  // Optional manual refresh button
  const refreshBtn = document.getElementById("refreshInvoices");
  if (refreshBtn) refreshBtn.addEventListener("click", fetchInvoices);

  // Handle file upload dynamically
  const uploadForm = document.querySelector("form[action='/upload']");
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(uploadForm);

      try {
        const res = await fetch("/upload", { method: "POST", body: formData });
        const data = await res.json();

        if (data.success && data.invoice) {
          addInvoiceRow(data.invoice);
          uploadForm.reset();
          alert("Invoice uploaded and added to table!");
        } else {
          alert("Failed to upload invoice!");
        }
      } catch (err) {
        console.error("Upload error:", err);
        alert("Upload failed!");
      }
    });
  }

  // Initial fetch
  fetchInvoices();
});

// Fetch all invoices and populate table
async function fetchInvoices() {
  try {
    const res = await fetch("/api/invoices");
    if (!res.ok) throw new Error("Failed to fetch invoices");
    const invoices = await res.json();

    const table = document.querySelector("table");
    if (!table) return;

    // Remove old rows except header
    table.querySelectorAll("tr:not(:first-child)").forEach(tr => tr.remove());

    invoices.forEach(inv => addInvoiceRow(inv));
  } catch (err) {
    console.error("Error fetching invoices:", err);
  }
}

// Add a single invoice row to table
function addInvoiceRow(inv) {
  const table = document.querySelector("table");
  if (!table) return;

  const tr = document.createElement("tr");
  tr.id = `invoice-${inv.id}`;
  if (inv.status.toLowerCase() === "rejected") tr.classList.add("rejected");

  tr.innerHTML = `
    <td>${inv.id}</td>
    <td>${inv.vendor_name || "-"}</td>
    <td>${inv.invoice_number || "-"}</td>
    <td>${inv.total_amount != null ? inv.total_amount.toFixed(2) : "-"}</td>
    <td>${inv.status}</td>
    <td>${inv.po ? inv.po.po_number : "-"}</td>
    <td>${inv.filename ? `<a href="/uploads/${inv.filename}" target="_blank">Open Invoice</a>` : "-"}</td>
    <td>${renderActions(inv)}</td>
  `;

  table.appendChild(tr);
}

// Generate action buttons for each invoice
function renderActions(inv) {
  if (inv.status.toLowerCase() === "pending" || inv.status.toLowerCase() === "unpaid") {
    return `
      <form class="action-form" style="display:inline-block; margin-right:4px;">
        <input type="hidden" name="invoice_id" value="${inv.id}" />
        <input type="hidden" name="action" value="approve" />
        <button type="button" class="btn-approve">Approve</button>
      </form>
      <form class="action-form" style="display:inline-block; margin-right:4px;">
        <input type="hidden" name="invoice_id" value="${inv.id}" />
        <input type="hidden" name="action" value="reject" />
        <button type="button" class="btn-reject">Reject</button>
      </form>
      <form class="action-form" style="display:inline-block;">
        <input type="hidden" name="invoice_id" value="${inv.id}" />
        <input type="hidden" name="action" value="force_match" />
        <input name="note" placeholder="PO id" style="width:60px;" />
        <button type="button">Force Match</button>
      </form>
    `;
  } else if (inv.status.toLowerCase() === "rejected") {
    return `
      <form class="action-form" style="display:inline-block;">
        <input type="hidden" name="invoice_id" value="${inv.id}" />
        <input type="hidden" name="action" value="delete" />
        <button type="button" class="btn-remove" style="background:#e74c3c;">Remove</button>
      </form>
    `;
  } else if (inv.status.toLowerCase() === "approved") {
    return `
      <form class="action-form" style="display:inline-block;">
        <input type="hidden" name="invoice_id" value="${inv.id}" />
        <input type="hidden" name="action" value="edit" />
        <button type="button" class="btn-edit">Edit</button>
      </form>
    `;
  }
  return "-";
}

// Handle all dynamic button clicks
document.addEventListener("click", async (e) => {
  const btn = e.target;
  if (!btn.closest(".action-form")) return;

  const form = btn.closest(".action-form");
  const invoiceId = form.querySelector("input[name='invoice_id']").value;
  let action = form.querySelector("input[name='action']").value;
  let note = form.querySelector("input[name='note']") ? form.querySelector("input[name='note']").value : null;

  if (btn.classList.contains("btn-edit")) {
    e.preventDefault();
    const newStatus = prompt("Enter new status (unpaid/rejected):", "unpaid");
    if (!newStatus || !["unpaid","rejected"].includes(newStatus.toLowerCase())) return alert("Invalid status!");
    action = newStatus.toLowerCase();
  } else if (btn.classList.contains("btn-remove")) {
    action = "delete";
  }

  try {
    const formData = new FormData();
    formData.append("invoice_id", invoiceId);
    formData.append("action", action);
    if (note) formData.append("note", note);

    let url = "/action";
    if (action === "delete") url = "/delete_invoice";

    const res = await fetch(url, { method: "POST", body: formData });
    if (res.ok) fetchInvoices();
    else alert("Action failed!");
  } catch (err) {
    console.error("Action error:", err);
    alert("Action failed!");
  }
});
