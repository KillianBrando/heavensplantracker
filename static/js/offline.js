let isSyncing = false;
let lastSyncTime = 0;  // Track the last sync time

// Utility function to throttle sync calls (allowing sync only once per X milliseconds)
function throttle(fn, limit) {
    return function (...args) {
        const now = Date.now();
        if (now - lastSyncTime >= limit) {
            lastSyncTime = now;
            fn.apply(this, args);
        } else {
            console.log("Sync throttled. Next sync allowed after", limit - (now - lastSyncTime), "ms");
        }
    };
}

// Throttled sync function
const throttledSyncExpenses = throttle(syncExpenses, 5000);  // Throttle for 5 seconds

// Event listener: Trigger sync when user comes back online
window.addEventListener('online', function() {
    console.log("Online event triggered, attempting to sync expenses...");
    
    if (!isSyncing) {
        throttledSyncExpenses();
    }
});

// Save new expenses to localStorage when offline
function saveExpenseLocally(expense) {
    let expenses = JSON.parse(localStorage.getItem('expenses')) || [];
    expense.synced = false;  // Mark new expense as unsynced
    expenses.push(expense);
    localStorage.setItem('expenses', JSON.stringify(expenses));
}

// Sync expenses to server when back online
function syncExpenses() {
    if (isSyncing) return;  // Prevent multiple sync calls

    console.log("Attempting to sync expenses...");
    isSyncing = true;

    let expenses = JSON.parse(localStorage.getItem('expenses')) || [];

    // Filter unsynced expenses
    let unsyncedExpenses = expenses.filter(expense => !expense.synced);

    if (unsyncedExpenses.length > 0) {
        fetch('/expenses/sync/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ expenses: unsyncedExpenses })
        }).then(response => {
            if (response.ok) {
                // Mark synced expenses as synced
                expenses = expenses.map(expense => {
                    if (!expense.synced) {
                        expense.synced = true;
                    }
                    return expense;
                });

                // Update localStorage with synced status
                localStorage.setItem('expenses', JSON.stringify(expenses));
                console.log("Expenses synced successfully!");
                alert('Expenses synced successfully!');
            } else {
                console.error("Failed to sync expenses, response not OK");
            }
        }).catch(error => {
            console.error("Sync failed:", error);
        }).finally(() => {
            isSyncing = false;
        });
    } else {
        console.log("No unsynced expenses to sync.");
        isSyncing = false;  // Reset syncing flag even if no unsynced expenses
    }
}

// Get CSRF token for Django
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Function to add expense (used when offline)
function addExpense(event) {
    event.preventDefault();
    const expenseData = {
        date: document.getElementById('id_date').value,
        amount: document.getElementById('id_amount').value,
        category: document.getElementById('id_category').value,
        description: document.getElementById('id_description').value
    };

    if (navigator.onLine) {
        document.getElementById('expense-form').submit();
    } else {
        saveExpenseLocally(expenseData);
        alert('Expense saved locally. It will sync when you are online.');
    }
}
