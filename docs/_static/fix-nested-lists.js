// Fix for nested list styling after page load
document.addEventListener('DOMContentLoaded', function () {
    console.log('Starting nested list fix...');

    // Function to completely remove bullets from an element
    function removeBullets(element) {
        element.style.setProperty('list-style', 'none', 'important');
        element.style.setProperty('list-style-type', 'none', 'important');
        element.style.setProperty('list-style-image', 'none', 'important');
        element.style.setProperty('list-style-position', 'outside', 'important');
        // Remove pseudo-element bullets
        element.style.setProperty('position', 'relative', 'important');

        // Add CSS to remove any ::before pseudo-elements that might be creating bullets
        const style = document.createElement('style');
        const className = 'no-bullets-' + Math.random().toString(36).substr(2, 9);
        element.classList.add(className);
        style.textContent = `
            .${className}::before,
            .${className}::after {
                display: none !important;
                content: none !important;
            }
        `;
        document.head.appendChild(style);
    }

    // PHASE 1: Find ALL task list items at ANY level and AGGRESSIVELY remove bullets
    const allTaskListItems = document.querySelectorAll('li.task-list-item, li:has(input[type="checkbox"]), li input.task-list-item-checkbox');
    console.log('Found task list items:', allTaskListItems.length);

    // Get parent li elements of checkboxes
    const checkboxes = document.querySelectorAll('input.task-list-item-checkbox, input[type="checkbox"]');
    checkboxes.forEach(function (checkbox) {
        const li = checkbox.closest('li');
        if (li) {
            console.log('removing bullets from task li:', li);
            removeBullets(li);
            li.style.setProperty('display', 'list-item', 'important');
            li.style.setProperty('margin-left', '0', 'important');
            li.style.setProperty('padding-left', '0', 'important');
        }
    });

    // PHASE 2: Find all ul elements that contain task items and remove their bullets too
    const taskUls = document.querySelectorAll('ul.contains-task-list, ul:has(li.task-list-item), ul:has(input[type="checkbox"])');
    taskUls.forEach(function (ul) {
        console.log('removing bullets from task ul:', ul);
        removeBullets(ul);
        ul.style.setProperty('padding-left', '1.5em', 'important');
        ul.style.setProperty('margin-left', '0', 'important');
    });

    // PHASE 3: Alternative approach - find ALL uls and check if they contain checkboxes
    const allUls = document.querySelectorAll('ul');
    allUls.forEach(function (ul) {
        const hasCheckboxes = ul.querySelector('input[type="checkbox"], input.task-list-item-checkbox');
        if (hasCheckboxes) {
            console.log('Found ul with checkboxes, removing bullets:', ul);
            removeBullets(ul);
            ul.style.setProperty('padding-left', '1.5em', 'important');

            // Also remove bullets from all li children that have checkboxes
            const lisWithCheckboxes = ul.querySelectorAll('li');
            lisWithCheckboxes.forEach(function (li) {
                const hasCheckbox = li.querySelector('input[type="checkbox"], input.task-list-item-checkbox');
                if (hasCheckbox) {
                    console.log('Removing bullets from li with checkbox:', li);
                    removeBullets(li);
                }
            });
        }
    });

    // PHASE 4: Handle regular lists (non-task lists)
    const regularUls = document.querySelectorAll('ul.simple:not(.contains-task-list)');
    regularUls.forEach(function (ul) {
        // Only apply bullets if this ul doesn't contain any checkboxes
        const hasCheckboxes = ul.querySelector('input[type="checkbox"], input.task-list-item-checkbox');
        if (!hasCheckboxes) {
            console.log('Applying bullets to regular ul:', ul);

            // Calculate depth
            let depth = 0;
            let parent = ul.parentElement;
            while (parent) {
                if (parent.tagName === 'UL') {
                    depth++;
                }
                parent = parent.parentElement;
            }

            const bulletType = depth === 0 ? 'disc' : depth === 1 ? 'circle' : 'square';
            ul.style.setProperty('list-style-type', bulletType, 'important');
            ul.style.setProperty('margin-left', '1.5em', 'important');
            ul.style.setProperty('padding-left', '0', 'important');

            // Apply to child li elements
            const regularLis = ul.querySelectorAll('li:not(.task-list-item)');
            regularLis.forEach(function (li) {
                const hasCheckbox = li.querySelector('input[type="checkbox"], input.task-list-item-checkbox');
                if (!hasCheckbox) {
                    li.style.setProperty('list-style-type', bulletType, 'important');
                    li.style.setProperty('display', 'list-item', 'important');
                }
            });
        }
    });

    console.log(' nested list styling applied!');
});
