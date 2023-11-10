function Sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function CreateNestedList(data) {
  const list = document.createElement('ul');

  for (let key in data) {
    const listItem = document.createElement('li');
    listItem.textContent = key;

    if (typeof data[key] === 'object' && data[key] !== null) {
      const nestedList = CreateNestedList(data[key]);
      listItem.appendChild(nestedList);
    } else {
      const itemValue = document.createElement('span');
      itemValue.textContent = " " + JSON.stringify(data[key]);
      listItem.appendChild(itemValue);
    }

    list.appendChild(listItem);
  }

  return list;
}

function GetCurrentDate() {
  const today = new Date();

  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
  const day = String(today.getDate()).padStart(2, '0');

  return `${year}-${month}-${day}`;
}
export {Sleep, CreateNestedList, GetCurrentDate}