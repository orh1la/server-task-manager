async function updateStatus() {
    let status = await fetch("/api/status").then(r => r.json());
    document.getElementById("cpu").innerText = status.cpu;
    document.getElementById("ram").innerText = status.ram;
    document.getElementById("disk").innerText = status.disk;
}

async function updateProcesses() {
    let procs = await fetch("/api/processes").then(r => r.json());
    let tbody = document.querySelector("#proc-table tbody");
    tbody.innerHTML = "";
    procs.forEach(p => {
        tbody.innerHTML += `<tr>
            <td>${p.pid}</td>
            <td>${p.name}</td>
            <td>${p.cpu}</td>
            <td>${p.ram}</td>
            <td><button onclick="kill(${p.pid})">End</button></td>
        </tr>`;
    });
}

async function checkAlert() {
    let res = await fetch("/api/auto_protect").then(r => r.json());
    let box = document.getElementById("alert-box");
    if(res.status==="ALERT") {
        box.style.background="red";
        box.innerText = `ALERT! Action: ${res.action} ${res.process||""}`;
    } else {
        box.style.background="";
        box.innerText="";
    }
}

async function kill(pid) {
    await fetch(`/api/kill/${pid}`,{method:"POST"});
}

setInterval(async () => {
    await updateStatus();
    await updateProcesses();
    await checkAlert();
}, 1000);
