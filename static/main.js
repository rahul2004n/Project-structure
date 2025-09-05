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
  tr.className = inv.status === "rejected" ? "rejected" : "";

  tr.innerHTML = `
    <td>${inv.id}</td>
    <td>${inv.vendor_name || "-"}</td>
    <td>${inv.customer || "-"}</td>
    <td>${inv.invoice_number || "-"}</td>
    <td>${inv.total_amount != null ? inv.total_amount.toFixed(2) : "-"}</td>
    <td>${inv.status}</td>
    <td>${inv.po ? inv.po.po_number : "-"}</td>
    <td>${renderActions(inv)}</td>
    <td>${inv.filename ? `<a href="/uploads/${inv.filename}" target="_blank">Open Invoice</a>` : "-"}</td>
  `;

  table.appendChild(tr);
}

// Generate action buttons for each invoice
function renderActions(inv) {
  if (inv.status === "pending") {
    return `
      <form action="/action" method="post" style="display:inline-block; margin-right:4px;">
        <input type="hidden" name="invoice_id" value="${inv.id}" />
        <input type="hidden" name="action" value="approve" />
        <button class="btn-approve">Approve</button>
      </form>
      <form action="/action" method="post" style="display:inline-block; margin-right:4px;">
        <input type="hidden" name="invoice_id" value="${inv.id}" />
        <input type="hidden" name="action" value="reject" />
        <button class="btn-reject">Reject</button>
      </form>
      <form action="/action" method="post" style="display:inline-block;">
        <input type="hidden" name="invoice_id" value="${inv.id}" />
        <input type="hidden" name="action" value="force_match" />
        <input name="note" placeholder="PO id" style="width:60px;" />
        <button>Force Match</button>
      </form>
    `;
  } else if (inv.status === "rejected") {
    return `
      <form action="/delete_invoice" method="post" style="display:inline-block;">
        <input type="hidden" name="invoice_id" value="${inv.id}" />
        <button class="btn-remove">Remove</button>
      </form>
    `;
  } else if (inv.status === "approved") {
    return "-";
  }

  return "-";
}
