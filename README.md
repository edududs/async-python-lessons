# Async Python Lessons

A comprehensive tutorial and examples collection for Python's `asyncio` library, demonstrating modern asynchronous programming patterns, task groups, futures, and synchronization primitives.

## 🚀 Overview

This repository contains practical examples and educational content for learning Python's `asyncio` module. The code demonstrates various concurrency patterns and synchronization mechanisms that are essential for building efficient asynchronous applications.

## 📚 What You'll Learn

### 1. **Basic Async Tasks**
- Understanding `async`/`await` syntax
- Using `asyncio.gather()` for concurrent execution
- Performance benefits of asynchronous programming

### 2. **TaskGroups** (Python 3.11+)
- Creating and managing groups of concurrent tasks
- Error handling and exception propagation
- Timeout management for task groups
- Conditional task creation based on runtime results
- Resource limiting with semaphores

### 3. **Futures**
- Manual control over asynchronous operations
- Exception handling in futures
- Timeout management
- Callback mechanisms
- Composing multiple futures with `gather()`

### 4. **Locks and Synchronization**
- **Lock**: Exclusive access to shared resources
- **Semaphore**: Limiting concurrent access
- **Event**: Signaling between tasks
- **Condition**: Complex synchronization scenarios
- **Barrier**: Coordinating multiple tasks
- **Queue**: Producer-consumer patterns

## 🛠 Requirements

- Python 3.11+ (for TaskGroup features)
- No external dependencies required

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/edududs/async-python-lessons.git
cd async-python-lessons
```

2. Run the examples:
```bash
python async-lessons.py
```

## 🏃‍♂️ Usage

### Running All Examples
```bash
python async-lessons.py
```

This will execute all three main sections:
1. TaskGroup examples
2. Future examples  
3. Lock and synchronization examples

### Running Specific Sections

You can also import and run specific sections by importing the file directly:

```python
import asyncio

# Import the entire module
exec(open('async-lessons.py').read())

# Run only TaskGroup examples
asyncio.run(task_groups())

# Run only Future examples
asyncio.run(main_future())

# Run only Lock examples
asyncio.run(demonstrate_locks())
```

## 📖 Code Examples

### Basic Async Tasks
```python
async def fetch_data(name: str, delay: float) -> dict:
    await asyncio.sleep(delay)
    return {"data": f"Result from {name}"}

# Execute concurrent tasks
results = await asyncio.gather(
    fetch_data("Task A", 1.0),
    fetch_data("Task B", 2.0),
    fetch_data("Task C", 1.5),
)
```

### TaskGroup with Error Handling
```python
async with asyncio.TaskGroup() as tg:
    task1 = tg.create_task(fetch_data("A", 1.0))
    task2 = tg.create_task(fetch_data("B", 2.0))
    # If any task fails, all tasks are cancelled
```

### Using Semaphore for Resource Limiting
```python
semaphore = asyncio.Semaphore(2)  # Only 2 concurrent tasks

async def limited_task(name: str):
    async with semaphore:
        # Only 2 tasks can execute this section simultaneously
        await asyncio.sleep(1.0)
        return f"Completed {name}"
```

## 🎯 Key Concepts Demonstrated

### TaskGroups
- **Structured concurrency**: All tasks in a group succeed or fail together
- **Exception propagation**: Any unhandled exception cancels all other tasks
- **Resource management**: Automatic cleanup of tasks
- **Timeout handling**: Global timeouts for entire task groups

### Futures
- **Manual control**: Create and resolve futures programmatically
- **Exception handling**: Set exceptions on futures
- **Callbacks**: React to future completion
- **Composition**: Combine multiple futures

### Synchronization Primitives
- **Lock**: Mutual exclusion for critical sections
- **Semaphore**: Control number of concurrent operations
- **Event**: Simple signaling mechanism
- **Condition**: Complex wait conditions with notifications
- **Barrier**: Synchronize multiple tasks at specific points
- **Queue**: Thread-safe communication between tasks

## 🔍 Performance Insights

The examples include timing measurements to demonstrate:
- How concurrent execution reduces total runtime
- The overhead of synchronization primitives
- The impact of different concurrency patterns

## 🤝 Contributing

Feel free to open issues or submit pull requests to improve the examples or add new patterns!

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📚 Additional Resources

- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [PEP 654 - Exception Groups and except*](https://peps.python.org/pep-0654/)
- [Real Python Async IO Guide](https://realpython.com/async-io-python/)

## 🏷️ Tags

`python` `asyncio` `concurrency` `async-await` `taskgroup` `futures` `synchronization` `locks` `semaphore` `queue` `barrier` `event` `condition`